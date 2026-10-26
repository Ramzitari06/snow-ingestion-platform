"""Point d'entree de l'application Snow Ingestion Platform."""
import pandas as pd
from fastapi import FastAPI

app = FastAPI()

@app.get("/customers")

def get_customers():

    df = pd.read_csv("data/raw/customers.csv")

    return df.to_dict(orient="records")

@app.get("/validations")
def get_validations():

    df = pd.read_csv("data/raw/validations.csv")

    return df.to_dict(orient="records")