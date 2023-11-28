import os

class KAFKA:
    HOST= os.environ.get('KAFKA_HOST')
    PORT=os.environ.get('KAFKA_PORT')
    TOPIC= os.environ.get('KAFKA_TOPIC')

class KAFKA_CONNECT:
    HOST= os.environ.get('KAFKA_CONNECT_HOST')

print("in config")