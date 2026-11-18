"""Point d'entrée de l'application Snow Ingestion Platform."""

import logging
from logging import config
import pandas as pd
from fastapi import FastAPI
from app.config.logger_config import logger_config
from app.services.load_data import load_dataframe
from app.services.Config_BDD import execute_ddl

from app.connectors.snowflake_connector import get_connection
from app.services.file_load import load_csv , truncate_table , merge_customers , merge_validations, save_load_history
from app.config.ParamLoad import paramLoad





confige = paramLoad() ;

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/customers")
def get_customers():

    param = confige["datasets"]["customers"] ;
    try:
    
        df = load_csv(param["file_path"])
        logger.info(
                    "Fichier customers.csv chargé avec succès. %s lignes trouvées.",
                    len(df)
                )
        return df.to_dict(orient="records")

    except FileNotFoundError:
        logger.error("Le fichier customers.csv est introuvable.")
        return {"error": "Fichier customers.csv introuvable"}

    except Exception as e:
        logger.exception(
                "Erreur lors de la lecture du fichier customers.csv"
                        )
        return {"error": str(e)}


@app.get("/validations")
def get_validations():
    param = confige["datasets"]["validations"] ;
    try:
        df = load_csv(param["file_path"])
        logger.info(
            "Fichier validations.csv chargé avec succès. %s lignes trouvées.",
            len(df)
        )

        return df.to_dict(orient="records")

    except FileNotFoundError:
        logger.error("Le fichier validations.csv est introuvable.")
        return {"error": "Fichier validations.csv introuvable"}

    except Exception as e:
        logger.exception(
            "Erreur lors de la lecture du fichier validations.csv"
        )
        return {"error": str(e)}


@app.get("/snowflake/test")
def test_connection():

    logger.info("Début du test de connexion Snowflake.")

    conn = None
    cursor = None

    try:

        conn = get_connection()
        logger.info("Connexion Snowflake établie.")

        cursor = conn.cursor()

        cursor.execute("SELECT CURRENT_VERSION()")

        result = cursor.fetchone()

        logger.info(
            "Version Snowflake récupérée : %s",
            result[0]
        )

        return {
            "status": "SUCCESS",
            "snowflake_version": result[0]
        }

    except Exception as e:

        logger.error(
            "Erreur lors du test de connexion Snowflake : %s",
            str(e)
        )

        return {
            "status": "ERROR",
            "message": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

@app.post("/load/customers")
def load_customers():

    param = confige["datasets"]["customers"]

    logger.info(
        "Début du chargement des données de customers dans Snowflake."
    )

    try:

        df = pd.read_csv(
            param["file_path"],
            delimiter=";"
        )

        logger.info(
            "Fichier lu avec succès. %s lignes détectées.",
            len(df)
        )

        if df.empty:

            logger.warning(
                "Le fichier customers.csv est vide."
            )

            save_load_history(
                "customers",
                param["staging_table"],
                param["target_table"],
                0,
                "WARNING",
                "Fichier vide",
                None,
                None
            )

            return {
                "status": "warning",
                "message": "Fichier vide"
            }

        truncate_table(param["staging_table"])

        load_dataframe(
            df=df,
            table_name=param["staging_table"]
        )

        merge_customers()

        save_load_history(
            "customers",
            param["staging_table"],
            param["target_table"],
            len(df),
            "SUCCESS",
            None,
            None,
            None
        )

        logger.info(
            "Chargement terminé avec succès. %s lignes chargées.",
            len(df)
        )

        return {
            "status": "success",
            "rows_loaded": len(df)
        }

    except Exception as e:

        logger.error(
            "Erreur lors du chargement de CUSTOMERS : %s",
            str(e)
        )

        save_load_history(
            "customers",
            param["staging_table"],
            param["target_table"],
            0,
            "FAILED",
            str(e),
            None,
            None
        )

        raise

@app.post("/load/validations")
def load_validations():

    param = confige["datasets"]["validations"]

    logger.info(
        "Début du chargement des données de validations dans Snowflake."
    )

    try:

        df = pd.read_csv(
            param["file_path"],
            delimiter=";"
        )

        logger.info(
            "Fichier lu avec succès. %s lignes détectées.",
            len(df)
        )

        if df.empty:

            logger.warning(
                "Le fichier validations.csv est vide."
            )

            save_load_history(
                "validations",
                param["staging_table"],
                param["target_table"],
                0,
                "WARNING",
                "Fichier vide",
                None,
                None
            )

            return {
                "status": "warning",
                "message": "Fichier vide"
            }

        truncate_table(
            param["staging_table"]
        )

        load_dataframe(
            df=df,
            table_name=param["staging_table"]
        )

        merge_validations()

        save_load_history(
            "validations",
            param["staging_table"],
            param["target_table"],
            len(df),
            "SUCCESS",
            None,
            None,
            None
        )

        logger.info(
            "Chargement terminé avec succès. %s lignes chargées.",
            len(df)
        )

        return {
            "status": "success",
            "rows_loaded": len(df)
        }

    except Exception as e:

        logger.error(
            "Erreur lors du chargement de VALIDATIONS : %s",
            str(e)
        )

        save_load_history(
            "validations",
            param["staging_table"],
            param["target_table"],
            0,
            "FAILED",
            str(e),
            None,
            None
        )

        raise
   
@app.post("/setup")
def setup_environment():

    try:

        execute_ddl()

        return {
            "status": "SUCCESS",
            "message": "Environnement Snowflake créé avec succès"
        }

    except Exception as e:

        logger.error(str(e))

        return {
            "status": "FAILED",
            "message": str(e)
        }