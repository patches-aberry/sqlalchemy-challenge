# Import the dependencies.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Hawaii Weather API<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<i>rain info 8/23/16 to 8/23/17.</i><br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"<i>station info</i><br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"<i>most active station 8/23/16 to 8/23/17.</i><br/><br/>"
        f"/api/v1.0/[start]<br/>"
        f"<i>output (max, min, mean) from input date to 8/23/17. use YYYY-MM-DD format. 1/1/10 to 8/23/17 for the results.</i><br/><br/>"
        f"/api/v1.0/[start]/[end]<br/>"
        f"<i>output (max, min, mean) for the date range. use YYYY-MM-DD format. 1/1/10 to 8/23/17 for the results.</i>"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    up_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= up_year).order_by(Measurement.date).all()


    all_precip_data = []
    for date, prcp in precip_data:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['precip'] = prcp
        all_precip_data.append(precip_dict)


    return jsonify(all_precip_data)

    session.close()


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    stations = []
    for id, station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict['id'] = id
        station_dict['station'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation
        stations.append(station_dict)

    return jsonify(stations)
    session.close()


@app.route("/api/v1.0/tobs")
def temps():
    session = Session(engine)
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    activity = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc())
    most_active = activity.first()[0]

    temp_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active).\
    filter(Measurement.date >= one_year).all()

    temps = []
    for date, tobs in temp_data:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['temp'] = tobs
        temps.append(temp_dict)

    return jsonify(temps)
    session.close()


@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    session = Session(engine)

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    start_temp_data = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    start_temps = []
    for max_temp, min_temp, avg_temp in start_temp_data:
        temp_dict = {}
        temp_dict['start date'] = start
        temp_dict['end date'] = recent_date
        temp_dict['max temp'] = max_temp
        temp_dict['min temp'] = min_temp
        temp_dict['avg temp'] = round(avg_temp,1)
        start_temps.append(temp_dict)

    return jsonify(start_temps)

    session.close()

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start, end):
    session = Session(engine)


    start_end_temp_data = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date.between(start, end)).all()

    start_end_temps = []
    for max_temp, min_temp, avg_temp in start_end_temp_data:
        temp_dict = {}
        temp_dict['start date'] = start
        temp_dict['end date'] = end
        temp_dict['max temp'] = max_temp
        temp_dict['min temp'] = min_temp
        temp_dict['avg temp'] = round(avg_temp,1)
        start_end_temps.append(temp_dict)
    return jsonify(start_end_temps)

    session.close()


if __name__ == '__main__':
    app.run(debug=True)