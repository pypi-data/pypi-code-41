# api/__init__.py

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    from api.models import User
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/users/', methods=['POST'])
    def users():
        username = str(request.data.get('username', ''))
        email = str(request.data.get('email', ''))
        if username and email:
            user = User(username=username, email=email)
            user.save()
            response = jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
            response.status_code = 201
            return response

    @app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def users_id_manipulation(id, **kwargs):
     # retrieve a user using it's ID
        user = User.query.filter_by(id=id).first()
        if not user:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == 'DELETE':
            user.delete()
            return {
            "message": "user {} deleted successfully".format(user.id) 
         }, 200
        
        elif request.method == 'PUT':
            username = str(request.data.get('username', ''))
            email = str(request.data.get('email', ''))
            user.username = username
            user.email = email
            user.save()
            response = jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
            response.status_code = 200
            return response
    
    return app