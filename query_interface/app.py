import os
from flask import Flask, render_template, request
from elasticsearch_dsl import connections, Q
from dotenv import load_dotenv

# load environment variables
load_dotenv('./../.env')                                # docker related
load_dotenv('.local.env', override=True)                # dev related

from models import Log


app = Flask(__name__)

connections.create_connection(hosts=f"http://{os.environ.get('ELASTIC_HOST')}:9200")

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/logs')
def get_logs():

    # search object on Log model
    search = Log.search()

    # create dsl query from request params
    exact_params = ['level', 'resourceId', 'spanId', 'traceId', 'commit']
    query = []

    for param in exact_params:
        param_value = request.args.get(param)
        if param_value:
            query.append(Q('match', **{param: param_value}))

    message = request.args.get('message')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    parent_resource_id = request.args.get('parentResourceId')

    if start_date:
        query.append(Q('range', timestamp={'gte': start_date, 'lte': end_date}))
    if message:
        query.append(Q('wildcard', message={'value': '*' + message + '*'}))
    if parent_resource_id:
        query.append(Q('match', metadata__parentResourceId=parent_resource_id))

    query = Q('bool', filter=query)

    # perform search from ES
    search = search.query(query)
    response = search.execute().to_dict()

    # return logs
    logs = [log['_source'] for log in response['hits']['hits']]
    return logs
