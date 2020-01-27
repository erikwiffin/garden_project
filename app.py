from collections import defaultdict
from datetime import datetime
import os

import click
from flask import Flask, jsonify, render_template
from gpiozero import MCP3008
import board
import adafruit_dht
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Measure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255))
    value = db.Column(db.Float())
    recorded_on = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def timestamp(self):
        return round(self.recorded_on.timestamp() * 1000)

    def to_json(self):
        return {
            'label': self.label,
            'value': self.value,
            'recorded_on': self.recorded_on.isoformat(),
        }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/measures')
def api_get_measures():
    measures = Measure.query.filter(Measure.recorded_on >= '2020-01-01').order_by(Measure.recorded_on).all()

    series = defaultdict(list)
    for m in measures:
        series[m.label].append([m.timestamp, m.value])

    data = [{
        'name': k,
        'data': v,
        'yAxis': int(k in ['soil-humidity', 'light']),
    } for k, v in series.items()]

    return jsonify(data)


@app.cli.command('initdb')
def initdb():
    db.create_all()


@app.cli.command('record')
def record():
    soil_sensor = MCP3008(0)
    light_sensor = MCP3008(1)
    air_sensor = adafruit_dht.DHT11(board.D18)

    try:
        air_temp_c = air_sensor.temperature
        air_humidity = air_sensor.humidity
        soil_humidity = soil_sensor.value
        light = light_sensor.value

        click.echo('-' * 20)
        click.echo(datetime.now().isoformat())
        click.echo('Writing measures...')

        db.session.add(Measure(label='air-temp-c', value=air_temp_c))
        db.session.add(Measure(label='air-humidity', value=air_humidity))
        db.session.add(Measure(label='soil-humidity', value=soil_humidity))
        db.session.add(Measure(label='light', value=light))

        db.session.commit()

        click.echo('Wrote 4 measures.')
    except RuntimeError as err:
        click.echo(err)
