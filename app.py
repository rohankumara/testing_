from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')

db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database Created !')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('DataBase Dropped ')


@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury',
                     planet_type='Class D',
                     home_star='Sol',
                     mass=3.228e23,
                     radius=1516,
                     distance=35.98e6)

    venus = Planet(planet_name='Venus',
                   planet_type='Class K',
                   home_star='Sol',
                   mass=4.68e23,
                   radius=3760,
                   distance=64.24e6)

    earth = Planet(planet_name='Earth',
                   planet_type='Class M',
                   home_star='Sol',
                   mass=5.972e24,
                   radius=3959,
                   distance=92.96e6)

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='Rohan',
                     last_name='Kumara',
                     email='rohan@rohan.com',
                     password='Test1234')
    db.session.add(test_user)
    db.session.commit()
    print('Db Seeded')


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/simple')
def simple():
    return jsonify(message='Hello from Planetary API with'), 200


@app.route('/notFound')
def not_found():
    return jsonify(error='Page was not found'), 400


@app.route('/parameter')
def parameter():
    name = request.args.get('name')
    age = int(request.args.get('age'))

    if age < 18:
        return jsonify(message=name + "you are not  enough old"), 401
    else:
        return jsonify(message=name + 'You are old enough')


@app.route('/variable/<string:name>/<int:age>')
def variable(name: str, age: int):
    if age < 18:
        return jsonify(message=name + "you are not  enough old"), 401
    else:
        return jsonify(message=name + 'You are old enough')


@app.route('/planet', methods=['GET'])
def planet():
    planet_list = Planet.query.all()
    result = planets_schema.dump(planet_list)
    return jsonify(result)


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email is already exists. '), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User Created Successfully'), 201

# Create DataBase Models


class User(db.Model):
    _tablename_ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    _tablename_ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == '__main__':
    app.run()
