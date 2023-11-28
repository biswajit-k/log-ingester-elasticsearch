import os
from elasticsearch_dsl import InnerDoc, Object, Document, Text, Date, Keyword


class LogMetaData(InnerDoc):
    parentResourceId = Keyword()

class Log(Document):
    level = Keyword()
    message = Text()
    resourceId = Keyword()
    timestamp = Date()
    traceId = Keyword()
    spanId = Keyword()
    commit = Keyword()
    metadata = Object(LogMetaData)

    class Index:
        name=os.environ.get('KAFKA_TOPIC')

