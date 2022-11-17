'''
Author: Daniel Abrahams
Synopsis: I am building a database service using SQLite which
allow users to access it via a REST API using HTTP methods such as POST and PUT.
These users must use a json web token to authenticate.
'''

#import outside Libs
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

#import standard libs
import uuid
import datetime
from functools import wraps

# here I create flask instance named app
app = Flask(__name__)

#set configuration variables
app.config['SECRET_KEY'] = 'Th1s1ss3cr3t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///////Users/princeabrahams/Desktop/Demo/CONSULTING/PrinceSportsCars/PrinceSportsCars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

#use the application object as a parameter to create an object of class SQLAlchemy.
db = SQLAlchemy(app)

# db.reflect()
# db.drop_all()

#create a class of users for those who use register endpoint
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)

#create a class of sports cars
class SportsCars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50),  nullable=False)
    model = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer)
    miles = db.Column(db.Integer)
    vin = db.Column(db.String(20), unique=True, nullable=False)

#create Cargurus sportcar class
class CarGurusSportsCar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carData = db.Column(db.String(3000),  nullable=False)

#create facebook sportscar class
class FaceBookSportsCar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carData = db.Column(db.String(3000),  nullable=False)

#create a token required decorator for endpoints that need authentication
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        ##pdb..set_trace()
        #retreive token and decode with based on user login
        token = request.headers['x-access-tokens']
        data = jwt.decode(token, app.config['SECRET_KEY'])
        current_user = Users.query.filter_by(public_id=data['public_id']).first()

        return f(current_user, *args, **kwargs)

    return decorator

@app.route('/register', methods=['GET', 'POST'])
def signup_user():

    #add new register user to DB
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'})

@app.route('/login', methods=['GET', 'POST'])
def login_user():

    #checks for all registered users in the Users table and check password
    #create token for authroized user

    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user = Users.query.filter_by(name=auth.username).first()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

@app.route('/user', methods=['GET'])
def get_all_users():

    #retreive all users in User Table

    users = Users.query.all()

    result = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin

        result.append(user_data)

    return jsonify({'users': result})

'''get all car gurus sports cars'''
@app.route('/cargurussportscars', methods=['GET', 'POST'])
@token_required
def get_carGurusSportsCar(current_user):

    carGurusSportsCar = CarGurusSportsCar.query.all()

    output = []

    for sportscar in carGurusSportsCar:
        sportscar_data = {}
        sportscar_data['carData'] = sportscar.carData
        output.append(sportscar_data)

    return jsonify({'list_of_cargurus_sportscars': output})

'''create cargurus sports car'''
@app.route('/cargurussportscar', methods=['POST', 'GET'])
@token_required
def create_carGurusSportsCar(current_user):

    #create a new sports car in sportscars table

    data = request.get_json()
    data = str(data)
    new_FaceBookSportsCar = FaceBookSportsCar(carData = data)
    db.session.add(new_FaceBookSportsCar)
    db.session.commit()

    return jsonify({'message': 'New Car Gurus Sports Car Created'})

'''retreive all facebook sportscars'''
@app.route('/facebooksportscars', methods=['GET', 'POST'])
@token_required
def get_FaceBookSportsCar(current_user):

    faceBookSportsCar = FaceBookSportsCar.query.all()

    output = []

    for sportscar in faceBookSportsCar:
        sportscar_data = {}
        sportscar_data['carData'] = sportscar.carData
        output.append(sportscar_data)

    return jsonify({'list_of_faceBook_sportscars': output})


'''create a new sports car from facebook'''
@app.route('/facebooksportscar', methods=['POST', 'GET'])
@token_required
def create_FaceBookSportsCar(current_user):

    data = request.get_json()
    data = str(data)
    new_FaceBookSportsCar = FaceBookSportsCar(carData = data)
    db.session.add(new_FaceBookSportsCar)
    db.session.commit()

    return jsonify({'message': 'New FaceBookSportsCar Created'})

'''retreive all sportscars'''
@app.route('/sportscars', methods=['GET', 'POST'])
@token_required
def get_sportscar(current_user):

    #retreive all cars in sportscars table

    sportscars = SportsCars.query.all()

    output = []

    for sportscar in sportscars:
        sportscar_data = {}
        sportscar_data['make'] = sportscar.make
        sportscar_data['model'] = sportscar.model
        sportscar_data['year'] = sportscar.year
        sportscar_data['miles'] = sportscar.miles
        sportscar_data['vin'] = sportscar.vin
        output.append(sportscar_data)

    return jsonify({'list_of_sportscars': output})

'''create a sports car'''
@app.route('/sportscar', methods=['POST', 'GET'])
@token_required
def create_sportscar(current_user):

    #create a new sports car in sportscars table

    data = request.get_json()

    new_sportscars = SportsCars(make=data['make'], model=data['model'], year=data['year'],
                                miles=data['miles'], vin=data['vin'])
    db.session.add(new_sportscars)
    db.session.commit()

    return jsonify({'message': 'New Sports Car Created'})

'''delete a sportscar from sportscars table based on vin'''
@app.route('/sportscars/<vin>', methods=['DELETE'])
@token_required
def delete_sportscar(current_user, vin):

    sportscars = SportsCars.query.filter_by(vin=vin).first()
    if not sportscars:
        return jsonify({'message': 'Sports Car does not exist'})

    db.session.delete(sportscars)
    db.session.commit()

    return jsonify({'message': 'Sportscars deleted'})


#db.create_all()
if __name__ == '__main__':
    app.run(debug=True)