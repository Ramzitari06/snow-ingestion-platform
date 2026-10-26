"""Point d'entree de l'application Snow Ingestion Platform."""
import pandas as pd
from fastapi import FastAPI
from app.connectors.snowflake_connector import get_connection

app = FastAPI()

@app.get("/customers")

def get_customers():

    df = pd.read_csv("data/raw/customers.csv")

    return df.to_dict(orient="records")

@app.get("/validations")
def get_validations():

    df = pd.read_csv("data/raw/validations.csv")

    return df.to_dict(orient="records")



@app.get("/snowflake/test")
def test_connection():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT CURRENT_VERSION()")

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {"snowflake_version": result[0]}
'''
@app.get("/read/{source_file}")
def read_file(source_file: str):

    df = pd.read_csv(f"data/raw/{source_file}.csv")

    return df.to_dict(orient="records") '''