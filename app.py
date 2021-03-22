import os
from datetime import timedelta
from flask import Flask, request, jsonify, session
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.sqlite"
app.secret_key = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=5)
CORS(app, supports_credentials = True)
db = SQLAlchemy(app)
ma = Marshmallow(app)
flask_bcrypt = Bcrypt(app)


class User(db.Model):
  user_id = db.Column(db.Integer, primary_key = True)
  user_name = db.Column(db.String(45), nullable = False)
  user_email = db.Column(db.String(100), nullable = False)
  user_password = db.Column(db.String(45), nullable = False)


  def __init__(self, user_name, user_email, user_password):
    self.user_name = user_name
    self.user_email = user_email
    self.user_password = user_password


class UserSchema(ma.Schema):
    class Meta:
        fields = ("user_id", "user_name", "user_emai", "user_password")


class Blog(db.Model):
  __tablename__ = "blogs"
  blog_id = db.Column(db.Integer, primary_key = True)
  blog_title = db.Column(db.String(100), nullable = False)


user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/')
def hello():
  return "Hello World"


@app.route('/api/v1/register_user', methods=['POST'])
def register():
  post_data = request.get_json()
  user_name = post_data.get('user_name')
  user_email = post_data.get('user_email')
  user_password = post_data.get('user_password')
  hashed_password = flask_bcrypt.generate_password_hash(user_password).decode('utf-8')
  new_user = User(user_name, user_email, user_password = hashed_password )
  db.session.add(new_user)
  db.session.commit()
  session.permanent = True
  session ['user_name'] = user_name
  print(session)
  return jsonify(user_schema.dump(new_user))


@app.route('/api/v1/get_users')
def get_users():
  all_users = User.query.all()
  return jsonify(users_schema.dump(all_users))

if __name__ == "__main__":
    app.debug = True
    app.run()