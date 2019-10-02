#!/usr/bin/env python
# coding: utf-8

# In[5]:


import sqlalchemy
from sqlalchemy import create_engine, inspect, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
Base= automap_base()
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
from flask import Flask, jsonify


# In[6]:


database_path='C:\workspace\Resources\hawaii.sqlite'
engine=create_engine(f'sqlite:///{database_path}')
conn= engine.connect()
Base.prepare(engine, reflect= True)
Base.classes.keys()
Measurement= Base.classes.measurement
Station= Base.classes.station


# In[7]:


app= Flask(__name__)


# In[9]:


@app.route("/")
def home():
    return (f"Welcome to Surfs Up in Hawaii!<br/>"
            f"Available route:<br/>"
            f"/api/v1.0/precipitation for precipitation data for the last year in the database<br/>"
            f"/api/v1.0/stations for list of stations from the dataset<br/>"
            f"/api/v1.0/tobs for a list of temperature observations for the previous year for most active station<br>"
            f"/api/v1.0/start_date/end_date to query for a period of time. Formating yyyy-mm-dd")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session= Session(engine)
    twelve_month_ago = dt.date(2017,8,23) - relativedelta(months=+12)
    now= dt.date(2017,8,23)
    prcp_12=session.query(Measurement.date, Measurement.prcp).        filter(Measurement.date <=now).        filter(Measurement.date >= twelve_month_ago).all()
    session.close()
    all_prcp=[]
    for date, prcp in prcp_12:
        prcp_dict={}
        prcp_dict["date"]=date
        prcp_dict["prcp"]=prcp
        all_prcp.append(prcp_dict)
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session= Session(engine)
    station_list= session.query(Station.station).all()
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temps():
    session= Session(engine)
    twelve_month_ago = dt.date(2017,8,23) - relativedelta(months=+12)
    now= dt.date(2017,8,23)
    station_counts=[Station.station, func.count(Measurement.tobs)]
    most_active=session.query(*station_counts).                filter(Station.station==Measurement.station).                group_by(Measurement.station).                order_by(func.count(Measurement.tobs).desc()).                limit(1).all()
    most_active_unzip = list(np.ravel(most_active))
    temp_12=session.query(Measurement.date, Measurement.tobs).                filter(Station.station==Measurement.station).                filter(Station.station==most_active_unzip[0]).                filter(Measurement.date <=now).                filter(Measurement.date >= twelve_month_ago).all()
    session.close()
    return jsonify(temp_12)

@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    session=Session(engine)
    now= dt.date(2017,8,23)
    start_list=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).                filter(Measurement.date >= start_date).filter(Measurement.date <= now).all()
    session.close()
    return jsonify(start_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    session= Session(engine)
    data_list=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    return jsonify(data_list)
    

if __name__=="__main__":
    app.run(debug=True)


# In[ ]:





# In[ ]:




