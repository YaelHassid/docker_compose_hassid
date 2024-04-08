import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import joblib
import sklearn
import pandas

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

@app.route("/")
def home():
    return "Hello from my Containerized Server"

@app.route('/teams', methods=['POST'])
def add_team():
    try:
        request_data = request.get_json()
        new_team = Team(
            year=request_data['year'],
            league=request_data['league'],
            obp=float(request_data['obp']),
            slg=float(request_data['slg']),
            ba=float(request_data['ba']),
            playoffs=request_data['playoffs'],
            g=float(request_data['g']),
            oobp=float(request_data['oobp']),
            oslg=float(request_data['oslg'])
        )
        db.session.add(new_team)
        db.session.commit()
        return "Team added successfully", 201
    except Exception as e:
        return str(e), 400

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
        'oslg': team.oslg
    } for team in teams}
    filename = 'model.sav'
    load_model = joblib.load(open(filename, 'rb'))
    #y_pred = load_model.predict(team_list)
    return jsonify(team_list)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555)
