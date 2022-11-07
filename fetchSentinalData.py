import json
import requests
from flask_marshmallow import Marshmallow
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from flask import Flask,jsonify,make_response,abort,request

import os
username = os.environ.get("USERNAME")
passw = os.environ.get("PASSWORD")
print(username)
print(passw)

app=Flask(__name__)

# connect to the API
@app.route("/")
def home():
   return "Data Fetch Sucessfully"


@app.route("/data", methods=['GET','POST'])
def sentinelData():
    request_data = request.get_json()

    startDate = request_data['StartDate']
    endDate = request_data['EndDate']
    api = SentinelAPI(username, passw)
    footprint = geojson_to_wkt(read_geojson('Sentinel.geojson'))

    products = api.query(footprint,
                         date=(startDate,endDate),
                         platformname='Sentinel-2',
                         cloudcoverpercentage=(0, 30))
    data=api.to_geojson(products)
    prod=dict(products)

    return make_response(jsonify(prod))

@app.errorhandler(Exception)
def resource_not_found(e):
    return jsonify(Please_Check_With_Following_Error=str(e))



if __name__ == "__main__":
 app.run(host="0.0.0.0",debug=True)
