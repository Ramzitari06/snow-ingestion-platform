import pandas as pd
import logging
from app.connectors.snowflake_connector import get_connection



logger = logging.getLogger(__name__)

def load_csv(path):
    logger.info("Lecture du fichier %s", path)

    df = pd.read_csv(path)

    logger.info(
        "Fichier %s chargé avec succès : %s lignes",
        path,
        len(df)
    )

    return df

def truncate_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def merge_customers():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        merge_sql = """
        MERGE INTO CUSTOMERS T
        USING STG_CUSTOMERS S
        ON T.CUSTOMER_ID = S.CUSTOMER_ID

        WHEN MATCHED THEN
            UPDATE SET
                T.FIRSTNAME = S.FIRSTNAME,
                T.LASTNAME = S.LASTNAME,
                T.CITY = S.CITY,
                T.CREATED_AT = S.CREATED_AT

        WHEN NOT MATCHED THEN
            INSERT (
                CUSTOMER_ID,
                FIRSTNAME,
                LASTNAME,
                CITY,
                CREATED_AT
            )
            VALUES (
                S.CUSTOMER_ID,
                S.FIRSTNAME,
                S.LASTNAME,
                S.CITY,
                S.CREATED_AT
            )
        ;
        """

        cursor.execute(merge_sql)

        conn.commit()

        logger.info("MERGE CUSTOMERS terminé")

    finally:

        cursor.close()
        conn.close()

def merge_validations():


    conn = get_connection()
    cursor = conn.cursor()

    try:

        merge_sql = """
        MERGE INTO VALIDATIONS T
        USING STG_VALIDATIONS S
        ON T.VALIDATION_ID = S.VALIDATION_ID

        WHEN MATCHED THEN
            UPDATE SET
                T.CUSTOMER_ID = S.CUSTOMER_ID,
                T.STATION = S.STATION,
                T.LINE = S.LINE,
                T.VALIDATION_DATETIME = S.VALIDATION_DATETIME

        WHEN NOT MATCHED THEN
            INSERT (
                VALIDATION_ID,
                CUSTOMER_ID,
                STATION,
                LINE,
                VALIDATION_DATETIME
            )
            VALUES (
                S.VALIDATION_ID,
                S.CUSTOMER_ID,
                S.STATION,
                S.LINE,
                S.VALIDATION_DATETIME
            )
        ;
        """

        cursor.execute(merge_sql)

        conn.commit()

        logger.info("MERGE VALIDATIONS terminé.")

    finally:

        cursor.close()
        conn.close()


def save_load_history(
    dataset_name: str,
    staging_table: str,
    target_table: str,
    rows_in_source: int,
    status: str,
    start_time,
    end_time,
    duration_seconds: float
):
    """
    Sauvegarde l'historique d'un chargement dans LOAD_HISTORY.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        query = """
        INSERT INTO LOAD_HISTORY (
            DATASET_NAME,
            STAGING_TABLE,
            TARGET_TABLE,
            ROWS_IN_SOURCE,
            STATUS,
            START_TIME,
            END_TIME,
            DURATION_SECONDS
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        cursor.execute(
            query,
            (
                dataset_name,
                staging_table,
                target_table,
                rows_in_source,
                status,
                start_time,
                end_time,
                duration_seconds
            )
        )

        conn.commit()

        logger.info(
            "Historique enregistré pour %s (%s lignes)",
            dataset_name,
            rows_in_source
        )

    except Exception as e:

        logger.error(
            "Erreur lors de l'enregistrement du LOAD_HISTORY : %s",
            str(e)
        )

        raise

    finally:

        cursor.close()
        conn.close()