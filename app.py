from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)



class ParkingMjesto(db.Model):
    __tablename__ = 'ParkingMjesto'
    id = db.Column(db.Integer, primary_key=True)
    etaza = db.Column(db.Integer, nullable=False)
    sekcija = db.Column(db.String(50), nullable=False)
    jeOkupirano = db.Column(db.Boolean, nullable=True)



class Vozilo(db.Model):
    __tablename__ = 'vozilo'
    id = db.Column(db.Integer, primary_key=True)
    registracija = db.Column(db.String(50), nullable=False)
    marka = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    vrijemeDolaska = db.Column(db.DateTime, default=datetime.now())
    parkingMjesto_id = db.Column(db.Integer, db.ForeignKey('ParkingMjesto.id'), nullable=True)
    parkingMjesto = db.relationship('ParkingMjesto', backref=db.backref('vozila', lazy=True))
    



class Karta(db.Model):
    __tablename__ = 'Karta'
    id = db.Column(db.Integer, primary_key=True)
    vrijemeDolaska = db.Column(db.DateTime, nullable=False)
    vrijemeOdlaska = db.Column(db.DateTime, nullable=False)
    vozilo_id = db.Column(db.Integer, db.ForeignKey('vozilo.id'), nullable=False)
    parkingMjesto_id = db.Column(db.Integer, db.ForeignKey('ParkingMjesto.id'), nullable=False)
    parkingMjesto = db.relationship('ParkingMjesto', backref=db.backref('karte', lazy=True))
    iznos = db.Column(db.Float, nullable=False)
    jePlaceno = db.Column(db.Boolean, nullable=False)


@app.route('/')
def index():
    parking_mjesta = ParkingMjesto.query.all()
    occupied_count = sum(1 for parking_mjesto in parking_mjesta if parking_mjesto.jeOkupirano)
    not_occupied_count = len(parking_mjesta) - occupied_count
    return render_template('index.html', parking_mjesta=parking_mjesta, occupied_count=occupied_count, not_occupied_count=not_occupied_count)



@app.route('/add_parking_mjesto', methods=['GET'])
def add_parking_mjesto_get():
    return render_template('parking_mjesto_form.html')


@app.route('/add_parking_mjesto', methods=['POST'])
def add_parking_mjesto_post():
    etaza = request.form['etaza']
    sekcija = request.form['sekcija']
    jeOkupirano = 'jeOkupirano' in request.form  # Checkbox returns 'on' if checked

    new_parking_mjesto = ParkingMjesto(etaza=etaza, sekcija=sekcija, jeOkupirano=jeOkupirano)
    db.session.add(new_parking_mjesto)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/record_parking', methods=['GET'])
def record_parking_get():
    return render_template('record_parking.html')

@app.route('/record_parking', methods=['POST'])
def record_parking_post():
    registracija = request.form['registracija']
    marka = request.form['marka_vozila']
    model = request.form['model_vozila']
    parking_mjesto_id = request.form['parking_mjesto_id']

    # Validacija parking mjesta
    parking_mjesto = ParkingMjesto.query.get(parking_mjesto_id)
    if not parking_mjesto:
        flash('Parkirno mjesto ne postoji.')
        return redirect(url_for('record_parking_get'))
    
    if parking_mjesto.jeOkupirano:
        flash('Parkirno mjesto je već zauzeto.')
        return redirect(url_for('record_parking_get'))
    
    parking_mjesto.jeOkupirano = True
    
    vozilo = Vozilo(registracija=registracija, marka=marka, model=model, parkingMjesto_id=parking_mjesto_id)
    db.session.add(vozilo)


    db.session.commit()

    flash('Parking recorded successfully!')
    return redirect(url_for('index'))

@app.route('/cars', methods=['GET'])
def cars_get():
    vozila = Vozilo.query.all()
    return render_template('vozila.html', vozila=vozila)


@app.route('/vozila/odjavi/<int:vozilo_id>', methods=['POST'])
def odjavi_vozilo(vozilo_id):
    vozilo = Vozilo.query.get(vozilo_id)
    if not vozilo:
        flash('Vozilo ne postoji.')
        return redirect(url_for('index'))
    
    parking_mjesto = ParkingMjesto.query.get(vozilo.parkingMjesto_id)
    if parking_mjesto:
        parking_mjesto.jeOkupirano = False

    vrijeme_dolaska = vozilo.vrijemeDolaska
    vrijeme_odlaska = datetime.now()
    trajanje_parkinga = (vrijeme_odlaska - vrijeme_dolaska).total_seconds() / 3600  # Duration in hours
    iznos = 2 * trajanje_parkinga  # Assuming the rate is 2 units per hour


    karta = Karta(
        vozilo_id=vozilo_id,
        parkingMjesto_id=vozilo.parkingMjesto_id,
        vrijemeDolaska = vrijeme_dolaska,
        vrijemeOdlaska = vrijeme_odlaska,
        iznos = iznos,
        jePlaceno = False
    )

    db.session.add(karta)
    db.session.delete(vozilo)
    db.session.commit()

    flash('Vozilo uspješno odjavljeno.')
    return redirect(url_for('index'))


@app.route('/karte', methods=['GET'])
def karte_get():
    karte = Karta.query.all()
    return render_template('billing.html', karte=karte)


@app.route('/karte/plati/<int:karta_id>', methods=['POST'])
def plati_kartu(karta_id):
    karta = Karta.query.get(karta_id)
    if not karta:
        flash('Karta ne postoji.')
        return redirect(url_for('karte_get'))
    
    if karta.jePlaceno:
        flash('Karta je već plaćena.')
        return redirect(url_for('karte_get'))
    
    karta.jePlaceno = True
    db.session.commit()

    flash('Karta uspješno plaćena.')
    return redirect(url_for('karte_get'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)