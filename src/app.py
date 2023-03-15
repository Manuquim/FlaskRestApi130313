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
from models import db, User,Characters,Planet,FavoritesChars,FavoritesPlanets

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
    if(user is not None):
        response_body = {
            "message": "OK ",
            "result" : user.serialize() }
    else:
        response_body = {"message": "user no existe "}

    return jsonify(response_body), 200


@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user=User.query.get(user_id)
    if(user is not None):
        db.session.delete(user)
        db.session.commit()
        response_body = {
        "message": "user borrado ",
        "user" : user.id}
    else:
        response_body={"message":"no existe este usuario"}

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


@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Characters.query.all()
    results = [character.serialize() for character in characters]
    response_body = {"message": "ok",
                     "total_records": len(results),
                     "results": results}
    return jsonify(response_body), 200


@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character=Characters.query.get(character_id)
    response_body = {
        "message": "OK ",
        "result" : character.serialize() }

    return jsonify(response_body), 200


@app.route('/characters', methods=['POST'])
def create_character():
    request_body=request.get_json()
    character=Character(name=request_body["name"],
              gender=request_body["gender"])
    db.session.add(character)
    db.session.commit()

    return jsonify(request_body), 200


@app.route('/planet', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [planet.serialize() for planet in planets]
    response_body = {"message": "ok",
                     "total_records": len(results),
                     "results": results}

    return jsonify(response_body), 200


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet_id(planet_id):
    planet = Planet.query.get(planet_id)
    result = planet.serialize()
    response_body = {"message": "ok",
                     "result": result}

    return jsonify(response_body), 200


@app.route('/planet', methods=['POST'])
def create_planet():
    request_body=request.get_json()
    planet=Planet(name=request_body["name"])
    db.session.add(planet)
    db.session.commit()

    return jsonify(request_body), 200


@app.route('/user/favoritesPlanets/<int:user_id>', methods=['GET'])
def get_favoritesPlanets(user_id):
    favorites = FavoritesPlanets.query.filter(FavoritesPlanets.user_id == user_id)
    results = [favorite.serialize() for favorite in favorites]
    response_body = {"message": "ok",
                    "total_records": len(results),
                    "results": results}

    return jsonify(response_body), 200


@app.route('/favorite/planet', methods=['POST'])
def add_favoritePlanet():
    request_body = request.get_json()
    favorite = FavoritesPlanets(user_id = request_body['user_id'],
                                    planet_id = request_body['planet_id'])
    db.session.add(favorite)
    db.session.commit()

    return jsonify(request_body), 200


@app.route('/favorite/character', methods=['POST'])
def add_favoriteCharacter():
    request_body = request.get_json()
    favorite = FavoritesChars(user_id = request_body['user_id'],
                              character_id = request_body['character_id'])
    db.session.add(favorite)
    db.session.commit()

    return jsonify(request_body), 200


@app.route("/favorite/Character/<int:favorite_id>", methods = ["DELETE"])
def delete_favoriteCharacter(favorite_id):
    favorite = FavoritesCharacters.query.get(favorite_id)
    if favorite is None:
        raise APIException('Favorite not found', status_code=404)
    db.session.delete(favorite)
    db.session.commit()

    return jsonify("Ok"), 200


@app.route("/favorite/Planet/<int:favorite_id>", methods = ["DELETE"])
def delete_favoritePlanet(favorite_id):
    favorites = FavoritesPlanets.query.get(favorite_id)
    if favorites is None:
        raise APIException('Favorite not found', status_code=404)
    db.session.delete(favorites)
    db.session.commit()
    return jsonify("Ok"), 200




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

