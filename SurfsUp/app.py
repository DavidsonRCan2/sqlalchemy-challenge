import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start --->To view values between a start and the last date, you must enter '/api/v1.0/YYYY-mm-dd'.<br/>"
        f"/api/v1.0/start/end  --->To view values between a start and end date, you must enter '/api/v1.0/YYYY-mm-dd/YYYY-mm-dd' with the start date first.<br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """retrieve only the last 12 months of data"""
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    one_year_query = session.query(measurement.date, measurement.prcp).filter(measurement.date > one_year).all()
    # one_year_df = pd.DataFrame(one_year_query)
    # one_year_df = one_year_df.set_index("date")
    # one_year_sorted = one_year_df.sort_index()
    session.close()
    
    one_year_list = []
    for date, prcp in one_year_query:
        one_year_dict = {}
        one_year_dict["date"] = date
        one_year_dict["prcp"] = prcp
        one_year_list.append(one_year_dict)


    return jsonify(one_year_list)


@app.route("/api/v1.0/stations")
def stations():
    '''
    This will give a list of stations available to review
    '''
    session = Session(engine)

    total_stations = session.query(station.name).all()

    session.close()

    all_stations = list(np.ravel(total_stations))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    '''
    This will give the temperatures and dates for the alstyear for the station
    with the most observations
    '''
    session = Session(engine)
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_most_active = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date.between(one_year,*last_date),\
            measurement.station == 'USC00519281').all()

    session.close()

    most_active_list = []
    for date, tobs in temp_most_active:
            tobs_dict ={}
            tobs_dict['date'] = date
            tobs_dict['tobs'] = tobs
            most_active_list.append(tobs_dict)
    return jsonify(most_active_list)
    
# create start and start/end route
# min, average, and max temps for a given date range
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine) 

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    # Create query for minimum, average, and max tobs where query date is greater than or equal to the date the user submits in URL
    start_date_tobs_results = session.query(func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    
    session.close() 

    # Create a list of min,max,and average temps that will be appended with dictionary values for min, max, and avg tobs queried above
    start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["start date"] = start
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs_values)

# Create a route that when given the start date only, returns the minimum, average, and maximum temperature observed for all dates greater than or equal to the start date entered by a user

@app.route("/api/v1.0/<start>/<end>")

# Define function, set start and end dates entered by user as parameters for start_end_date decorator
def Start_end_date(start, end):
    session = Session(engine)

    """Return a list of min, avg and max tobs between start and end dates entered"""
    
    # Create query for minimum, average, and max tobs where query date is greater than or equal to the start date and less than or equal to end date user submits in URL

    start_end_date_tobs_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()
  
    # Create a list of min,max,and average temps that will be appended with dictionary values for min, max, and avg tobs queried above
    start_end_tobs_date_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["start date"] = start
        start_end_tobs_date_dict["end date"] = end
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date_values.append(start_end_tobs_date_dict) 
    

    return jsonify(start_end_tobs_date_values)

if __name__ == "__main__":
    app.run(debug=True)