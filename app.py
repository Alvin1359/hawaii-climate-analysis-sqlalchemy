# Import dependencies and modules
import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Variables
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home_page():
    print("Request for 'home_page'")
    return (f'Welcome to "Hawaii Surfs Up!" API<br/>'
            f'<br/>'
            f'Available Routes:<br/>'
            f'---------------------<br/>'
            f'# Precipitation measurements<br/>'
            f'/api/v1.0/precipitation<br/>'
            f'<br/>'
            f'# List of stations<br/>'
            f'/api/v1.0/stations<br/>'
            f'<br/>'
            f'# Temperature observations (TOBS) for the previous year of the most active station: USC00519281<br/>'
            f'/api/v1.0/tobs<br/>'
            f'<br/>'
            f'----------------------<br/>'
            f'Date Format: yyyy-mm-dd<br/>'
            f'# Temperature minimum, maximum and average for dates greater than start date (e.g. ../2010-01-01)<br/>'
            f'/api/v1.0/yyyy-mm-dd<br/>'
            f'<br/>'
            f'# Temperature minimum, maximum and average for dates between start and end date (e.g. ../2010-01-01/2017-08-23)<br/>'
            f'/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>'
            f'----------------------<br/>'
            f'*Data available for period between 2010-01-01 and 2017-08-23<br/>')

@app.route("/api/v1.0/precipitation")
def precipitation_page():
    print("Request for precipitation_page")
    
    #Return a dictionary of all dates and precipitations
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all measurements
    results = session.query(Measurement).all()

    # Close the Query
    session.close()

    # Create dictionary using date as key and precipitation as value
    precipitation_data = []

    for result in results:
        precipitation_data_dict = {}
        precipitation_data_dict["date"] = result.date
        precipitation_data_dict["prcp"] = result.prcp
        precipitation_data.append(precipitation_data_dict)

    # Jsonify results
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations_page():
    print("Request for station_page")
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    # Close the Query
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs_page():
    print("Request for tobs_page")
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all measurements
    tobs_result = session.query(Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date > year_ago).all()
    
    # Close the Query
    session.close()

    tobs_list = list(np.ravel(tobs_result))

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def datestart_page(start):
    print("Request for datestart_page")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create sel containing functions for minimum, maximum and average
    sel = [Measurement.date,
        func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]

    # Query database for results greater than starting date 
    results = session.query(*sel).filter(Measurement.date >= start).group_by(Measurement.date).all()

    # Close the Query
    session.close()

    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def date_start_end_page(start, end):
    print("Request for date_start_end_page")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create sel containing functions for minimum, maximum and average
    sel = [Measurement.date,
        func.min(Measurement.tobs),
       func.max(Measurement.tobs),
       func.avg(Measurement.tobs)]

    # Query database for results greater than starting date and less than ending date 
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    # Close the Query
    session.close()

    return jsonify(results)


if __name__ == "__main__":
	app.run(debug=True)