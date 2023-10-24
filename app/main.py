import os
from fastapi import FastAPI
from mangum import Mangum

from . import solar_scheme

# fix to see autogen docs in lamdba
stage = os.environ.get('STAGE', None)
openapi_prefix = f"/{stage}" if stage else "/"

app = FastAPI(title="SolarScheme", openapi_prefix=openapi_prefix)
handler = Mangum(app)


@app.get("/")
def run_solar_scheme():
    df = solar_scheme.run_solar_scheme()
    return df.reset_index().to_dict('records')



