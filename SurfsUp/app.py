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
        f"/api/v1.0/stations"
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

    total_stations = session.query(station.station).distinct().count()

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
    




if __name__ == "__main__":
    app.run(debug=True)