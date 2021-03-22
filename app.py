import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials = True)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
  __tablename__ = "users"
  user_id = db.Column(db.Integer, primary_key = True)
  user_name = db.Column(db.String(45), nullable = False)
  user_email = db.Column(db.String(100), nullable = False)
  user_password = db.Column(db.String(45), nullable = False)

  def __init__(self, user_name, user_email, user_password):
    self.user_name = user_name
    self.user_email = user_email
    self.user_password = user_password

class Blog(db.Model):
  __tablename__ = "blogs"
  blog_id = db.Column(db.Integer, primary_key = True)
  blog_title = db.Column(db.String(100), nullable = False)


class UserSchema(ma.Schema):
    class Meta:
        fields = ("users_id", "users_name", "users_emai", "users_password")

user_schema = UserSchema()
users_schema = UserSchema(many=True)



@app.route('/')
def hello():
  return "Hello World"

if __name__ == "__main__":
    app.debug = True
    app.run()