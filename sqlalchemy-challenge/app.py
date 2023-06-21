# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#################################################
# Database Setup
#################################################
app = Flask(__name__)

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True, autoload_with=engine)




# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Create an instance of Flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define the homepage route
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data as JSON."""
    # Query the database for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').all()

    # Create a dictionary with date as the key and prcp as the value
    precipitation_data = {date: prcp for date, prcp in results}

    # Return the precipitation data as JSON
    return jsonify(precipitation_data)

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset as JSON."""
    # Query the database for the list of stations
    results = session.query(Station.station, Station.name).all()

    # Create a list of dictionaries with station and name
    station_list = []
    for station, name in results:
        station_dict = {'station': station, 'name': name}
        station_list.append(station_dict)

    # Return the station list as JSON
    return jsonify(station_list)

# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations of the most active station for the previous year as JSON."""
    # Query the database for the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).\
        first()

    # Query the database for the temperature observations of the most active station for the previous year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date >= '2016-08-23').all()

    # Create a list of dictionaries with date and tobs
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {'date': date, 'tobs': tobs}
        tobs_list.append(tobs_dict)

    # Return the temperature observations as JSON
    return jsonify(tobs_list)

# Define the start and start-end date route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    """Return the minimum, average, and maximum temperatures for a specified start or start-end range as JSON."""
    # Query the database for the temperature statistics
    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    # Create a dictionary with temperature statistics
    temp_stats_dict = {
        'min_temp': results[0][0],
        'avg_temp': results[0][1],
        'max_temp': results[0][2]
    }

    # Return the temperature statistics as JSON
    return jsonify(temp_stats_dict)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
