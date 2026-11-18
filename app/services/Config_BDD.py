from app.connectors.snowflake_connector import get_connection
import logging
from app.config.ParamLoad import paramLoad

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


config = paramLoad()

def execute_ddl():

    conn = get_connection()
    cursor = conn.cursor()
    param = config["Script"]["sql"] ;
    try:

        with open(param["file_path"], "r") as file:
            sql_script = file.read()

        statements = sql_script.split(";")

        for statement in statements:

            statement = statement.strip()

            if statement:
                cursor.execute(statement)
                print(f"Executed : {statement[:50]}")

        conn.commit()

        print("Infrastructure créée avec succès")

    finally:

        cursor.close()
        conn.close()


if __name__ == "__main__":
    execute_ddl()