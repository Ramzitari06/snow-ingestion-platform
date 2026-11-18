import yaml 

def paramLoad():
    with open("app/config/dataset.yaml", "r", encoding="utf-8") as file:
        params = yaml.safe_load(file)
    return params