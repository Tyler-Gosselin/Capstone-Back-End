import os
from datetime import timedelta
from flask import Flask, json, request, jsonify, session
from flask.globals import session
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
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique = False, nullable=False)
    email = db.Column(db.String(100), unique = False,  nullable=False)
    password = db.Column(db.String(45), unique = False, nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "email", "password")


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique = False,  nullable=False)
    author = db.Column(db.String(40), unique = False,  nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, title, author):
        self.title = title
        self.author = author


class BlogSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "author")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)


@app.route('/')
def hello():
    return "Hello World"


@app.route('/api/register-user', methods=['POST'])
def register():
    post_data = request.get_json()
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    hashed_password = flask_bcrypt.generate_password_hash(
        password).decode('utf-8')
    new_user = User(username, email, password = hashed_password)
    db.session.add(new_user)
    db.session.commit()
    session.permanent = True
    session['username'] = username
    print(session)
    return jsonify(user_schema.dump(new_user))


@app.route('/api/get-users')
def get_users():
    all_users = User.query.all()
    return jsonify(users_schema.dump(all_users))


@app.route('/api/create-blog', methods=['POST'])
def create_blog():
    post_data = request.get_json()
    title = post_data.get('title')
    author = post_data.get('author')
    new_blog = Blog(title, author)
    db.session.add(new_blog)
    db.session.commit()
    return jsonify(blog_schema.dump(new_blog))


@app.route('/api/get-blogs')
def get_blogs():
    all_blogs = Blog.query.all()
    return jsonify(blogs_schema.dump(all_blogs))


@app.route('/api/edit-blog/<blog_id>', methods=['PATCH'])
def edit_blog(blog_id):
    blog = Blog.query.filter_by(id=blog_id).first()
    blog.title = request.json.get('title')
    blog.author = request.json.get('author')
    db.session.commit()
    return jsonify(blog_schema.dump(blog))


@app.route('/api/login', methods=['POST'])
def login():
    post_data = request.get_json()
    db_user = User.query.filter_by(
        username=post_data.get('username')).first()
    if db_user is None:
        return "User NOT Found", 401
    password = post_data.get('password')
    db_user_hashed_password = db_user.password
    valid_password = flask_bcrypt.check_password_hash(
        db_user_hashed_password, password)
    if valid_password:
        session.permanent = True
        session['username'] = post_data.get('username')
        return jsonify('User Verified')
    return "Password Invalid", 401


@app.route('/api/logged-in')
def logged_in():
    if 'username' in session:
        db_user = User.query.filter_by(username=session['username']).first()
        if db_user:
            return jsonify('User Logged in Via Cookie')
        else:
            return jsonify('Session exists, but user does not exist')
    else:
        return jsonify('Not logged in')


@app.route('/api/delete-user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify('User Deleted')
    return "User NOT Found", 404


@app.route('/api/delete-blog/<id>', methods=['DELETE'])
def delete_blog(id):
    blog = Blog.query.filter_by(id=id). first()
    if blog:
        db.session.delete(blog)
        db.session.commit()
        return jsonify('Blog Deleted')
    return "Blog Not Found", 404


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify('Logged Out')


if __name__ == "__main__":
    app.debug = True
    app.run()
