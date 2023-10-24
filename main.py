from src import solar_scheme
from typing import Union
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def run_solar_scheme():
    df = solar_scheme.run_solar_scheme()
    return df.reset_index().to_dict('records')
