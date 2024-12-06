# Import the dependencies
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table
from models import Measurement, Station

#################################################
# Database Setup
#################################################
DATABASE_URL = "sqlite:///Resources/hawaii.sqlite"
engine = create_engine(DATABASE_URL)

# reflect an existing database into a new model
Base = declarative_base()
Base.metadata.reflect(engine)

# reflect the tables
Base.metadata.reflect(engine)

# Save references to each table
measurement_table = Base.metadata.tables['measurement']
station_table = Base.metadata.tables['station']

# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)
session = Session()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

#################################################
# Flask Routes
#################################################
# Route 1: Precipitation Data
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date >= '2017-08-23') \
        .order_by(Measurement.date).all()

    # Create a dictionary with date as the key (converted to string) and prcp as the value
    precipitation_dict = {date.strftime('%Y-%m-%d'): prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Route 2: Stations
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    stations_data = session.query(Station.station).all()

    # Convert the query results into a list of stations
    stations_list = [station[0] for station in stations_data]

    return jsonify(stations_list)


# Route 3: Temperature Observations for Station USC00519281
@app.route("/api/v1.0/tobs")
def tobs():
    # Set the station ID directly to USC00519281
    station_id = 'USC00519281'

    # Query temperature observations for the station 'USC00519281'
    tobs_data = session.query(Measurement.date, Measurement.tobs) \
        .filter(Measurement.station == 'USC00519281') \
        .filter(Measurement.date >= '2017-08-23') \
        .all()

    # If no data is found, return an error message
    if not tobs_data:
        return jsonify({"error": f"No temperature data found for station {station_id}"}), 404

    # Create a list of temperature observations
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)



# Route 4: Temperature Stats from a Start Date
@app.route("/api/v1.0/<start>")
def start_date(start='2016-08-24'):
    # Query the temperature data for the start date and beyond
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
        .filter(Measurement.date >= start).all()

    # If no data is found for the given start date, return an error message
    if not temps:
        return jsonify({"error": f"No temperature data found for the date {start}"}), 404

    # Return the results as JSON
    return jsonify({
        "TMIN": temps[0][0],
        "TAVG": temps[0][1],
        "TMAX": temps[0][2]
    })


# Route 5: Temperature Stats from Start to End Date
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start='2016-08-24', end='2017-08-23'):
    # Query the temperature data for the start and end date range
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
        .filter(Measurement.date >= start) \
        .filter(Measurement.date <= end).all()

    # If no data is found for the given date range, return an error message
    if not temps:
        return jsonify({"error": f"No temperature data found for the date range {start} to {end}"}), 404

    # Return the results as JSON
    return jsonify({
        "TMIN": temps[0][0],
        "TAVG": temps[0][1],
        "TMAX": temps[0][2]
    })


if __name__ == "__main__":
    app.run(debug=True)