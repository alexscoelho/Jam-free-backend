"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap # APIException es un method
from admin import setup_admin
from models import db, User, Teacher, Student, Files
#from models import Person
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET') 
)

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Simple extension
app.config['JWT_SECRET_KEY'] = 'jammfree-app'  
jwt = JWTManager(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# Create a new user 
@app.route('/user', methods=['POST'])
def create_user():
    try:
        body = request.get_json()
        print(request)
        if body is None:
            raise APIException("You need to specify the request body as a json object", 400)
        # Validations
        if 'email' not in body:
            raise APIException("You need to specify an email", 400)
        if 'first_name' not in body:
            raise APIException("You need to specify a first name", 400)
        if 'last_name' not in body:
            raise APIException("You need to specify a last name", 400)
        if 'password' not in body:
            raise APIException("You need to specify a password", 400)
        if 'account_type' not in body:
            raise APIException("You need to specify account type", 400)
        if 'language' not in body:
            raise APIException("You need to specify your language", 400)
        if 'customer_id' not in body:
            raise APIException("You need to specify your customer id", 400)
        # check if this email already exists
        user_exists = User.query.filter_by(email=body['email']).first()
        # Exception when user exists
        if user_exists is not None: 
            raise APIException("email is in use", 400)
        user = User(first_name=body['first_name'], last_name=body['last_name'], email=body['email'], password=body['password'], account_type=body['account_type'], language=body['language'], customer_id=body["customer_id"])
        db.session.add(user)
        db.session.commit()
        return jsonify("Success", 200)
    except Exception as e:
        return jsonify(e.__dict__)

# Single Users
@app.route('/user/<int:user_id>', methods=['POST', 'GET'])
@jwt_required
def handle_single_user(user_id):
    target_user = User.query.get(user_id)
    
    if request.method == 'POST':
        try:
            body=request.form
            # Get all form data fields
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            language = request.form["language"]
            instrument = request.form["instrument"]
            level = request.form["level"]
            description = request.form["description"]
            profile_picture = request.files["profile_picture"]

            print(request.form["first_name"])
            
            # Modify an user
            if target_user is None:
                raise APIException('User not found', 404)
            if "first_name" in body:
                target_user.first_name = first_name
            if "last_name" in body:
                target_user.last_name = last_name
            if "language" in body:
                target_user.language = language
                

            # check if this username already exists
            # username_exists = User.query.filter_by(username=body['username']).first()
            # Exception when user exists
            # if username_exists is not None: 
            #     raise APIException("username is in use", 400)
            if "username" in body:
                username_exists = User.query.filter_by(username=username).first()
                if username_exists is not None: 
                    raise APIException("username is in use", 400)
                target_user.username = username
            
            if "instrument" in body:
                target_user.instrument = instrument  
            if "level" in body:
                target_user.level = level
            if "description" in body:
                target_user.description = description  

            if "username" in body:
                username_exists = User.query.filter_by(username=username).first()
                if username_exists is not None: 
                    raise APIException("username is in use", 400)
                target_user.username = username

            
            if profile_picture is not None:
                print('picture attached')
                # upload box to cloudinary
                profile_picture_upload_result = cloudinary.uploader.upload( 
                    profile_picture ,
                    options = {
                        "use_filename": True  # use filename as public id on cloudinary
                    }
                )
                target_user.profile_picture = profile_picture_upload_result['secure_url']
                        
            db.session.commit()
            
            # return jsonify(target_user.serialize()),200
            return jsonify("Success", 200)
        except Exception as e:
            return jsonify(e.__dict__)  
    
    # Get an user
    if request.method == 'GET':
        if target_user is None:
            raise APIException('User not found', 404)
        return jsonify(target_user.serialize(), 200)
    return jsonify("Invalid Method", 404)

# Delete user
@app.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required
def delete_user(user_id):
    target_user = User.query.get(user_id)
    if target_user is None:
        raise APIException('User not found', 404)
    db.session.delete(target_user)
    db.session.commit()
    return jsonify("Success", 200)



# Get all users
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    if users is None:
        raise APIException('There are no users', 404)
    all_users = list(map(lambda x: x.serialize(), users ))
    return jsonify(all_users, 200)


# Filter Files
@app.route('/file/<int:file_id>', methods=['GET'])
def get_file(file_id):
    single_file = Files.query.get(file_id) # query to the db to get the file
    if single_file is None:
        raise APIException('File not found', 404)
    return jsonify(single_file.serialize(), 200) # Getting the file


# Get all files
@app.route('/files', methods=['GET'])
# @jwt_required
def get_all_files():
    files = Files.query.all() # Get all files
    if files is None:
        raise APIException('There are no files', 404)
    all_files = list(map(lambda x: x.serialize(), files )) # el x es el element, param files
    return jsonify(all_files, 200)


# Delete file
@app.route('/file/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    target_file = Files.query.get(file_id)
    if target_file is None:
        raise APIException('File not found', 404)
    db.session.delete(target_file)                  # Delete method
    db.session.commit()                             # save changes
    return jsonify("Success", 200)


# Create File
@app.route('/file', methods=['POST'])
def create_file(): #encapsular accion
    body = request.get_json() # encapsula el paquete enviado del postman, recibe json y lo convierte al lenguaje del diccionario
    print(body)
    single_file = Files(instrument=body['instrument'], type_file=body['typeFile'], level=body['level'], language=body['language'], url=body['url'], user_id=body['userId'], title=body['title'])
    db.session.add(single_file) # adding user
    db.session.commit() # commiting what we add
    return jsonify(body, 200)

# Edit File
@app.route('/file/<int:file_id>', methods=['PUT'])
def edit_file(file_id):
    body = request.get_json()
    single_file = Files.query.get(file_id) # get a unique file
    if single_file is None: # handling error
        raise APIException('File not found', status_code = 404)
    if "instrument" in body:
        single_file.instrument = body['instrument']
    if "typeFile" in body:
        single_file.type_file = body['typeFile']
    if "level" in body:
        single_file.level = body['level']  
    if "language" in body:
        single_file.language = body['language']
    if "url" in body:
        single_file.url = body['url']
    if "title" in body:
        single_file.title = body['title']
    db.session.commit()
    return jsonify(body, 200)

    

    
# Login
# # Provide a method to create access tokens. The create_jwt()
# # function is used to actually generate the token
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    email = params.get('email', None)
    password = params.get('password', None)

    
    login_user = User.query.filter_by(email= email).first()
    # print("login_user:", login_user)
    

    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if email != login_user.email or password != login_user.password:
        return jsonify({"msg": "Bad email or password"}), 401
    
# Identity can be any data that is json serializable
    ret = {
        'jwt': create_jwt(identity=email),
        'userId': login_user.id
    }
    return jsonify(ret), 200

# # # Protected routes
# @app.route('/main', methods=['GET'])
# @jwt_required
# def protected():
#     # Access the identity of the current user with get_jwt_identity
#     return jsonify({'hello_from': get_jwt_identity()}), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
