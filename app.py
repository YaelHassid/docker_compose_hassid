import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import joblib
import sklearn
import pandas as pd

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask import render_template

db_username = os.environ['DB_USERNAME']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
db_uri = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy()
db.init_app(app)

class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.String(50), nullable=False)
    league = db.Column(db.String(50), nullable=False)
    obp = db.Column(db.Float, nullable=False)
    slg = db.Column(db.Float, nullable=False)
    ba = db.Column(db.Float, nullable=False)
    playoffs = db.Column(db.String(50), nullable=False)
    g = db.Column(db.Float, nullable=False)
    oobp = db.Column(db.Float, nullable=False)
    oslg = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.Float, nullable=False)


class AddTeamForm(FlaskForm):
    year = StringField('Year', validators=[DataRequired()])
    league = SelectField('League', choices=[('AL', 'AL'), ('NL', 'NL')], validators=[DataRequired()])
    obp = FloatField('OBP', validators=[DataRequired()])
    slg = FloatField('SLG', validators=[DataRequired()])
    ba = FloatField('BA', validators=[DataRequired()])
    playoffs = StringField('Playoffs', validators=[DataRequired()])
    g = FloatField('G', validators=[DataRequired()])
    oobp = FloatField('OOBP', validators=[DataRequired()])
    oslg = FloatField('OSLG', validators=[DataRequired()])
    submit = SubmitField('Add Team')


@app.route("/")
def home():
    return "Hello from my Containerized Server"

@app.route('/add_team',  methods=['GET', 'POST'])
def add_team():
    if request.method == 'POST':
        # Get data from the form
        year = request.form['year']
        league = request.form['league']
        obp = float(request.form['obp'])
        slg = float(request.form['slg'])
        ba = float(request.form['ba'])
        playoffs = request.form['playoffs']
        g = float(request.form['g'])
        oobp = float(request.form['oobp'])
        oslg = float(request.form['oslg'])

        data = {'year': [year], 'league': [league], 'obp': [obp], 'slg': [slg], 'ba': [ba],
                'playoffs': [playoffs], 'g': [g], 'oobp': [oobp], 'oslg': [oslg]}
        df = pd.DataFrame(data)
        model = joblib.load('model.sav')

        pred = model.predict(df)


        new_team = Team(
            year=year,
            league=league,
            obp=obp,
            slg=slg,
            ba=ba,
            playoffs=playoffs,
            g=g,
            oobp=oobp,
            oslg=oslg,
            prediction=pred[0]  # You can update this with the actual prediction
        )

        db.session.add(new_team)
        db.session.commit()
        return "Team added successfully", 201

    else:
        return render_template('add_team.html')

@app.route('/teams')
def show_teams():
    teams = Team.query.all()
    team_list = {team.id: {
        'year': team.year,
        'league': team.league,
        'obp': team.obp,
        'slg': team.slg,
        'ba': team.ba,
        'playoffs': team.playoffs,
        'g': team.g,
        'oobp': team.oobp,
        'oslg': team.oslg,
        'prediction': team.prediction
    } for team in teams}

    return jsonify(team_list)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555)
