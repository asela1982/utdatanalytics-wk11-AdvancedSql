
#################################################
# import dependencies
#################################################

import pandas as pd
import numpy as np
from datetime import date
import sqlalchemy
from sqlalchemy import and_
from sqlalchemy.sql import label
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# database setup 
#################################################

# Create an engine for the hawaii.sqlite database
engine = create_engine("sqlite:///hawaii.sqlite", echo=False)

# Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to the db tables
Station = Base.classes.stations
Measurement = Base.classes.measurements

# Create a session
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/") # http://google.com/ # 127.0.0.1/ # root route
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Climate API!<br/>"

        f"<strong>Available Routes:</strong><br/>"

        f"/api/v1.0/precipitation"
        f"- Dates and Temperature observations for the year 2016<br/>"

        f"/api/v1.0/stations"
        f"- List of stations<br/>"

        f"/api/v1.0/tobs"
        f"- List of Temperature Observations (tobs) for the year 2016<br/>"

        f"/api/v1.0/startdate"
        f"- Enter the start date in YYYY-MM-DD format <br/>"

        f"/api/v1.0/startdate/enddate"
        f"- Enter the start and end dates in YYYY-MM-DD format"
    )

@app.route("/api/v1.0/precipitation")
def get_prec():
    """Query for the dates and temperature observations 
    from the last year.Convert the query results to a 
    Dictionary using `date` as the key and `tobs` as the value.
    Return the json representation of your dictionary"""

    result_proxy = session.query(Measurement).\
                    filter(func.strftime('%Y', Measurement.date) == '2016').all()
    
    # Create a dictionary from the row data and append to the results list
    results = []

    for row in result_proxy:
        result_dict = {}
        result_dict[str(row.date)] = row.tobs
        results.append(result_dict)

    return jsonify(results)


@app.route("/api/v1.0/stations")
def get_stations():
    """Return a json list of stations from the dataset."""

    result_proxy = session.query(Station).all()
    # Create a dictionary from the row data and append to the results list
    
    results = []

    for row in result_proxy:
        results.append(row.name)
    return jsonify(results)


@app.route("/api/v1.0/tobs")
def get_tobs():
    """Return a json list of Temperature 
    Observations (tobs) for the previous year"""
    
    result_proxy = session.query(Measurement).\
                    filter(func.strftime('%Y', Measurement.date) == '2016').all()
    
    results = []

    for row in result_proxy:
        results.append(row.tobs)
    return jsonify(results)


@app.route("/api/v1.0/<startdate>")
def start(startdate):
    """When given the start only, calculate `TMIN`, `TAVG`, 
     and `TMAX` for all dates greater than 
     and equal to the start date."""

    year, month, day = map(int, startdate.split('-')) # map(function_to_apply, list_of_inputs)
    start_date = date(year, month, day) # calculate the matching begin date from the previous year

    sel = [label('tmin',func.min(Measurement.tobs)),\
           label('tmax',func.max(Measurement.tobs)),\
           label('tavg',func.avg(Measurement.tobs))]

    result_proxy = session.query(*sel).\
                   filter(Measurement.date >=start_date).all()
    
    results = []

    for row in result_proxy:
        result_dict = {}
        result_dict['tmin'] = row[0]
        result_dict['tmax'] = row[1]
        result_dict['tavg'] = row[2]
        results.append(result_dict)
    return jsonify(results)


@app.route("/api/v1.0/<startdate>/<enddate>")
def start_end(startdate,enddate):
    """When given the start and the end date, calculate the `TMIN`, 
      `TAVG`, and `TMAX` for dates between 
      the start and end date inclusive."""

    year, month, day = map(int, startdate.split('-')) # map(function_to_apply, list_of_inputs)
    start_date = date(year, month, day) 
    year, month, day = map(int, enddate.split('-')) # map(function_to_apply, list_of_inputs)
    end_date = date(year, month, day) 

    sel = [label('tmin',func.min(Measurement.tobs)),\
           label('tmax',func.max(Measurement.tobs)),\
           label('tavg',func.avg(Measurement.tobs))]

    result_proxy = session.query(*sel).\
                   filter(and_(Measurement.date >=startdate,\
                    Measurement.date<=enddate))

    results = []

    for row in result_proxy:
        result_dict = {}
        result_dict['tmin'] = row[0]
        result_dict['tmax'] = row[1]
        result_dict['tavg'] = row[2]
        results.append(result_dict)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True) #debug true only in development