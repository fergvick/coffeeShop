import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


## ROUTES
'''
ENDPOINT
    GET /drinks
        - public endpoint
        - Expected to return status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200
    except:
        abort(404)

'''
ENDPOINT
    GET /drinks-detail
        - Gets all drinks details
        - Requires the 'get:drinks-detail' permission
        - Expected to return status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200
    except:
        abort(404)

'''
ENDPOINT
    POST /drinks
        - Create a new row in the drinks table
        - Requires the 'post:drinks' permission
        - Expected to return status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):

    data = request.get_json()
    if 'title' and 'recipe' not in data:
        abort(422)

    title = data['title']
    recipe_json = json.dumps(data['recipe'])

    drink = Drink(title=title, recipe=recipe_json)

    drink.insert()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
ENDPOINT
    PATCH /drinks/<id>
        where <id> is the existing model id
        - Edits drink
        - Requires the 'patch:drinks' permission
        - Expected to return status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
        - Expected to respond with a 404 error if <id> is not found
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):

    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    data = request.get_json()
    if 'title' in data:
        drink.title = data['title']

    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })



'''
ENDPOINT
    DELETE /drinks/<id>
        where <id> is the existing model id
        - Deletes drink
        - Require the 'delete:drinks' permission
        - Expected to return status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
        - Expected to respond with a 404 error if <id> is not found
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):

    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink.id
    })


## Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }),400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not Found'
    }),404

@app.errorhandler(405)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }),405

@app.errorhandler(422)
def uproccessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'Unproccessable'
    }),422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }),500

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code

