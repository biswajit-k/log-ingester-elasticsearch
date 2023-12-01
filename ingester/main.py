import json
import requests

from fastapi import FastAPI
from contextlib import asynccontextmanager
from kafka import KafkaProducer
from dotenv import load_dotenv

# load environment variables
load_dotenv('./../.env')                                # docker related
load_dotenv('.local.env', override=True)                # dev related

from config import KAFKA, KAFKA_CONNECT


@asynccontextmanager
async def lifespan(app:  FastAPI):

    # set kafka-connect configurations through post request
    config = {
        "name": "elasticsearch-sink",
        "config": {
            "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
            "tasks.max": "1",
            "topics": KAFKA.TOPIC,
            "key.ignore": "true",
            "schema.ignore": "true",
            "connection.url": f"http://elastic:9200",
            "type.name": "_doc",
            "name": "elasticsearch-sink",
            "value.converter": "org.apache.kafka.connect.json.JsonConverter",
            "value.converter.schemas.enable": "false"
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    url = f'http://{KAFKA_CONNECT.HOST}:8083/connectors'

    response = requests.post(url=url,
                json=config, headers=headers)

    if response.ok:
        print("...kafka-connect config set...")
    else:
        print('...unable to set kafka-connect config...')


    # create the json data serializer producer and connect to kafka
    app.state.producer = KafkaProducer(bootstrap_servers=[f"{KAFKA.HOST}:{KAFKA.PORT}"],
                api_version=(3,4,0), value_serializer=lambda m: json.dumps(m).encode('ascii'))
    print("producer created")
    yield
    # send all buffer requests before closing connection
    app.state.producer.flush()
    app.state.producer.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post('/logs')
async def ingest_logs(log: dict):
    app.state.producer.send(KAFKA.TOPIC, log)
    return {"message": "Log Received"}