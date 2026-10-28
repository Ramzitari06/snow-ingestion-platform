"""Point d'entrée de l'application Snow Ingestion Platform."""

import logging
import pandas as pd
from fastapi import FastAPI
from app.config.logger_config import logger_config
from app.services.load_data import load_dataframe

from app.connectors.snowflake_connector import get_connection
from app.services.file_load import load_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/customers")
def get_customers():

    try:
    
        df = load_csv("data/raw/customers.csv")
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

    try:
        df = load_csv("data/raw/validations.csv")
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
    df = pd.read_csv("data/raw/customers.csv" , delimiter=";")
    load_dataframe(
        df=df,
        table_name="CUSTOMERS"
    )

    return {
        "status": "success",
        "rows_loaded": len(df)
    }

@app.post("/load/validations")
def load_validations():
    df = pd.read_csv("data/raw/validations.csv" , delimiter=";")
    load_dataframe(
        df=df,
        table_name="VALIDATIONS"
    )

    return {
        "status": "success",
        "rows_loaded": len(df)
    }

       