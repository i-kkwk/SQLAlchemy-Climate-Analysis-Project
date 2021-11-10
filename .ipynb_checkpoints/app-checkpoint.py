# import Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func ,inspect
import datetime as dt
from flask import Flask, jsonify


engine  = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

Base = automap_base()

Base.prepare(engine, reflect = True)

measurement = Base.classes.measurement
station = Base.classes.station



session = Session(engine)
                                      

app = Flask(__name__)


first_date = session.query(measurement.date).order_by(measurement.date).first()
last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

@app.route("/")
def Home():
    return  (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )




@app.route("/api/v1.0/precipitation")
def percipitation():
    
    session = Session(engine)
    first_date = session.query(measurement.date).order_by(measurement.date).first()
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    prcp_data = (session.query(measurement.date, func.avg(measurement.prcp)).filter(measurement.date>= year_ago).order_by(measurement.date).all())
    results_prcp = list(np.ravel(prcp_data))

        
    return jsonify(results_prcp)

@app.route("/api/v1.0/stations")
def stations():
    
    session  = Session(engine)
    total_station = session.query(station.name).all()
    result_station = list(np.ravel(total_station))
    
    return jsonify(result_station)
    
@app.route("/api/v1.0/tobs")
def tobs():
    
    first_date = session.query(measurement.date).order_by(measurement.date).first()
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()    
    m_active_st = session.query(measurement.station,func.count(measurement.station)).\
              group_by(measurement.station).\
              order_by(func.count(measurement.station).desc()).all()
    best_station = m_active_st[0][0]
    session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
              filter(measurement.station == best_station).all()
    return jsonify(best_station)
    
@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(measurement.date, measurement.tobs, measurement.station).filter(measurement.date > year_ago).order_by(measurement.date).all())

    tempData = []
    
    for result in results:
        tempDict = {result.date: result.tobs, "station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)


def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", measurement.date) == date).all()
    
daily_normals("01-01")

@app.route("/api/v1.0/temperature/<start>")
@app.route("/api/v1.0/temperature/<start>/<end>")
def start(start = None, end = None):
    session = Session(engine)
    
    startDate = "2017-05-03"
    endDate = "2017-05-13"

    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    startDate  = dt.datetime.strptime(startDate, '%Y-%m-%d')
    trip_Length = 12

    date_List = [dt.datetime.strftime(startDate + dt.timedelta(days = x), '%m-%d') 
            for x in range(0, trip_Length)]

    # Loop through the list of %m-%d strings and calculate the normals for each date
    trip_normals = [daily_normals(date) for date in date_List]
    daily = list(np.ravel(trip_normals))
    
    return jsonify(daily)

if __name__ == '__main__':
    app.run(debug=True)
    
    
