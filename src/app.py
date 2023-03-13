"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin

#importa modelos creados en models
from models import db, User,Characters
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_users():
    users=User.query.all()
    #serialize convierte un objeto python en un string,
    #esta definido en models.py
    results=[user.serialize() for user in users]

    response_body = {
        "message": "OK ",
        "total_records": len(results),
        "results" :results  }

    return jsonify(response_body), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user=User.query.get(user_id)
    response_body = {
        "message": "OK ",
        "result" : user.serialize() }

    return jsonify(response_body), 200

@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user=User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    response_body = {
        "message": "user borrado ",
        "user" : user.id}

    return jsonify(response_body), 200

@app.route('/user', methods=['POST'])
def create_users():
    request_body=request.get_json()
    user=User(email=request_body["email"],
              password=request_body["password"],
              is_active=request_body["is_active"])
    db.session.add(user)
    db.session.commit()

    return jsonify(request_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
