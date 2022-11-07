import datetime
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from flask import jsonify, Flask, request,make_response,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from tkinter import *

from tkinter import ttk

import os
picfolder=os.path.join('static','styles')

username = os.environ.get("USERNAME")
passw = os.environ.get("PASSWORD")
print(username)
print(passw)
api = SentinelAPI(username, passw)
footprint = geojson_to_wkt(read_geojson('/home/lt-339/PycharmProjects/tudip/Practicals/SentinelProject/Sentinel.geojson'))

app = Flask(__name__)
db = SQLAlchemy(app)
ma = Marshmallow(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Sentinel_Data.sqlite'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['UPLOAD_FOLDER']=picfolder



class Sentinel_Data(db.Model):
    product_id = db.Column(db.Unicode(10),primary_key=True)
    fileName = db.Column(db.String(500))
    cloudCovPer = db.Column(db.Numeric)
    st_date = db.Column(db.DateTime)
    en_date = db.Column(db.DateTime)

    def __int__(self,id,product_id,filename,cloudCover,st_date,en_date):
        self.product_id=product_id
        self.fileName=filename
        self.cloudCovPer=cloudCover
        self.st_date=st_date
        self.en_date=en_date




class Schema(ma.Schema):
    class Meta:
        fields = ("product_id", "fileName", "cloudCovPer", "st_date", "en_date")


my_Data = Schema(many=True)


# ------------------------------------------------------------------------
try:
        products = api.query(footprint,
                             date=('20190625', '20190627'),
                             platformname='Sentinel-2',
                             cloudcoverpercentage=(0, 30))
        pro_dict=dict(products)

        for i, (prod_id, j) in enumerate(products.items()):
            props = j.copy()
            props["id"] = prod_id
            pro_id = prod_id
            ccp = props["cloudcoverpercentage"]
            begin_pos = props["beginposition"]
            fname = props["filename"]
            end_pos = props["endposition"]

            database = Sentinel_Data(product_id=pro_id, fileName=fname, cloudCovPer=ccp, st_date=begin_pos, en_date=end_pos)

            db.session.add(database)
            db.session.commit()
except :
    print(" ")
@app.route("/data2", methods=['GET','POST'])
def sentinelData():
    request_data = request.get_json()

    startDate = request_data['StartDate']
    endDate = request_data['EndDate']
    sattalite=request_data['Sattalite']
    api = SentinelAPI(username, passw)
    footprint = geojson_to_wkt(read_geojson('/home/lt-339/PycharmProjects/tudip/Practicals/SentinelProject/Sentinel.geojson'))
    if sattalite.startswith('Sentinel'):
        if int(startDate) < int(endDate):
            products = api.query(footprint,
                                 date=(startDate,endDate),
                                 platformname=sattalite,
                                 cloudcoverpercentage=(0, 30))
            data=api.to_geojson(products)
            prod=dict(products)

            return make_response(jsonify(prod))
        else:
            return make_response(jsonify("Enter Correct Date:","StartDate must be less than EndDate"))
    else:
        return jsonify("Please Enter the Correct Satellite Name Please Refered :","https://sentinels.copernicus.eu/web/sentinel/home" )

@app.route("/")
def home():

    return "Data Fetch Successfully"


@app.route("/data")
def show():
    try:
        data = Sentinel_Data.query.all()
        res = my_Data.dump(data)
        p=make_response(jsonify("Sentinel_Data",res),200)
        return p
    except:
        print("Error")
@app.route("/dat",methods=["GET"])
def sample(ids):
    return jsonify(ids)
@app.route("/data/<ids>",methods=["GET"])
def fetProduct(ids):

        pro_d=Sentinel_Data.query.filter_by(product_id=ids).all()
        if len(pro_d)==1:
            res = my_Data.dump(pro_d)
            return make_response(jsonify(res))
        else:
            return make_response(jsonify("Data not found"))

@app.route("/data/delete/<ids>", methods=["DELETE"])
def data_delete(ids):
        data = Sentinel_Data.query.filter_by(product_id=ids).all()
        if len(data)==1:
            for prId in data:
              db.session.delete(prId)
              db.session.commit()
            return make_response(jsonify("Data Delete Successfully"))
        else:
            return make_response(jsonify("Data Not Exits"))
@app.route("/date", methods=['GET', 'POST'])
def date_example():
    if request.method == "POST":

        sattalite = request.form.get('Sattalite')
        startDate = request.form.get('date')
        endDate = request.form.get('date1')
        year, month, day = str(startDate).split("-")
        y,m,d=str(endDate).split("-")
        StartDate=year+month+day
        EndDate=y+m+d
        sat=str(sattalite)
        if sat.startswith('Sentinel'):
            if int(StartDate) < int(EndDate) :
                products = api.query(footprint,
                                     date=(StartDate, EndDate),
                                     platformname=sat,
                                     cloudcoverpercentage=(0, 30))
                data = api.to_geojson(products)
                prod = dict(products)

                return make_response(jsonify(prod))
            else:
                return jsonify("Enter Valid Date")
        else:
            return jsonify("Please Enter the Correct Satellite Name")
    else:
        pic=os.path.join(app.config['UPLOAD_FOLDER'],'ASpot_Sentinel-6.jpg')
        return render_template("Data.html",user_image=pic)

@app.errorhandler(Exception)
def resource_not_found(e):
    return jsonify(Please_Check_With_Following_Error=str(e))

if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0',debug=True)
