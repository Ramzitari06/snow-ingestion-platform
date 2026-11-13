from app.connectors.snowflake_connector import get_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_dataframe(df, table_name ):

    conn = get_connection()
    cursor = conn.cursor()
    logger.info("Chargement de %s avec clé primaire", table_name)
    try:

        for _, row in df.iterrows():

            values = tuple(row)

            placeholders = ",".join(["%s"] * len(values))

            query = (
                f"INSERT INTO {table_name} "
                f"VALUES ({placeholders})"
            )

            cursor.execute(query, values)

        conn.commit()

    finally:

        cursor.close()
        conn.close()