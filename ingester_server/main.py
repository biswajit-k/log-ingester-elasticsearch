from fastapi import FastAPI, Request
from elasticsearch_dsl import connections
import os
from dotenv import load_dotenv

from models import Log, LogMetaData


app = FastAPI()

# load environment variables
load_dotenv('.prod.env')


# create connection with ES
connections.create_connection(hosts=os.environ.get('ES_HOST_URL'))


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post('/logs')
async def ingest_log(request: Request):
    data = await request.json()

    # pick out log metadata from the request body
    log_metadata = data.pop('metadata')
    metadata = LogMetaData(**log_metadata)

    log = Log(metadata=metadata, **data)
    log.save()