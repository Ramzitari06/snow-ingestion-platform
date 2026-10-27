import pandas as pd
import logging

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