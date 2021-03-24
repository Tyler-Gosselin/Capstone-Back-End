import os
from datetime import timedelta
from flask import Flask, json, request, jsonify, session
from flask.globals import session
from flask_marshmallow.schema import Schema
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.sqlite"
app.secret_key = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(days=14)
CORS(app, supports_credentials=True)
db = SQLAlchemy(app)
ma = Marshmallow(app)
flask_bcrypt = Bcrypt(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(45), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.String(45), nullable=False)

    def __init__(self, user_name, user_email, user_password):
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password


class UserSchema(ma.Schema):
    class Meta:
        fields = ("user_id", "user_name", "user_emai", "user_password")


class Blog(db.Model):
    __tablename__ = "blogs"
    blog_id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(100), nullable=False)

    def __init__(self, blog_title):
        self.blog_title = blog_title


class BlogSchema(ma.Schema):
    class Meta:
        fields = ("blog_id", "blog_title")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)


@app.route('/')
def hello():
    return "Hello World"


@app.route('/api/v1/register-user', methods=['POST'])
def register():
    post_data = request.get_json()
    user_name = post_data.get('user_name')
    user_email = post_data.get('user_email')
    user_password = post_data.get('user_password')
    hashed_password = flask_bcrypt.generate_password_hash(
        user_password).decode('utf-8')
    new_user = User(user_name, user_email, user_password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    session.permanent = True
    session['user_name'] = user_name
    print(session)
    return jsonify(user_schema.dump(new_user))


@app.route('/api/v1/get-users')
def get_users():
    all_users = User.query.all()
    return jsonify(users_schema.dump(all_users))


@app.route('/api/v1/create-blog', methods=['POST'])
def create_blog():
    post_data = request.get_json()
    blog_title = post_data.get('blog_title')
    new_blog = Blog(blog_title)
    db.session.add(new_blog)
    db.session.commit()
    return jsonify(blog_schema.dump(new_blog))


@app.route('/api/v1/get-blogs')
def get_blogs():
    all_blogs = Blog.query.all()
    return jsonify(blogs_schema.dump(all_blogs))


@app.route('/api/v1/login', methods=['POST'])
def login():
    post_data = request.get_json()
    db_user = User.query.filter_by(
        user_name=post_data.get('user_name')).first()
    if db_user is None:
        return "User NOT Found", 401
    password = post_data.get('user_password')
    db_user_hashed_password = db_user.user_password
    valid_password = flask_bcrypt.check_password_hash(
        db_user_hashed_password, password)
    if valid_password:
        session.permanent = True
        session['user_name'] = post_data.get('user_name')
        return jsonify('User Verified')
    return "Password Invalid", 401


@app.route('/api/v1/logged-in')
def logged_in():
    if 'user_name' in session:
        db_user = User.query.filter_by(user_name=session['user_name']).first()
        if db_user:
            return jsonify('User Logged in Via Cookie')
        else:
            return jsonify('Session exists, but user does not exist')
    else:
        return jsonify('Nope!')


@app.route('/api/v1/delete-user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter_by(user_id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify('User Deleted')
    return "User NOT Found", 404


@app.route('/api/v1/delete-blog/<id>', methods=['DELETE'])
def delete_blog(id):
  blog = Blog.query.filter_by(blog_id = id). first()
  if blog:
    db.session.delete(blog)
    db.session.commit()
    return jsonify('Blog Deleted')
  return "Blog Not Found", 404


if __name__ == "__main__":
    app.debug = True
    app.run()
