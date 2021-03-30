import os
from datetime import timedelta
from flask import Flask, request, jsonify, session
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_bcrypt import Bcrypt
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATBASE_URL') or "sqlite:///app.sqlite"
app.secret_key = os.environ.get('SECRET_KEY') or "SUPER_SECRET"
app.permanent_session_lifetime = timedelta(days=14)

CORS(app, supports_credentials=True)
db = SQLAlchemy(app)
ma = Marshmallow(app)
flask_bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=False,  nullable=False)
    password = db.Column(db.String(45), unique=False, nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship("User", backref="blogs")

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    # blogs = fields.Nested(lambda:BlogSchema(exclude=["id", "user_id"]))
    blogs = fields.List(fields.Nested(
        lambda: BlogSchema(only=["title", "content", "user_id"])))


class BlogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Blog
        include_fk = True

    author = fields.Nested(lambda: UserSchema(exclude=["password"]))


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
    new_user = User(username, email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    session.permanent = True
    session['username'] = username
    return jsonify({"message": 'User Verified', "user_id": new_user.id})
    


@app.route('/api/get-users')
def get_users():
    all_users = User.query.all()
    return jsonify(users_schema.dump(all_users))


@app.route('/api/create-blog', methods=['POST'])
def create_blog():
    post_data = request.get_json()
    title = post_data.get('title')
    content = post_data.get('content')
    user_id = post_data.get('user_id')
    new_blog = Blog(title, content, user_id)
    db.session.add(new_blog)
    db.session.commit()
    return jsonify(blog_schema.dump(new_blog))


@app.route('/api/get-blogs')
def get_blogs():
    all_blogs = Blog.query.all()
    return jsonify(blogs_schema.dump(all_blogs))

@app.route('/api/get-blog/<id>')
def get_blog(id):
    blog= Blog.query.get(id)
    return blog_schema.jsonify(blog)
    

@app.route('/api/edit-blog/<id>', methods=['PATCH'])
def edit_blog(id):
    blog = Blog.query.filter_by(id=id).first()
    blog.title = request.json.get('title')
    blog.content = request.json.get('content')
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
        return jsonify({"message": 'User Verified', "user_id": db_user.id})
    return "Password Invalid", 401


@app.route('/api/logged-in')
def logged_in():
    if 'username' in session:
        db_user = User.query.filter_by(username=session['username']).first()
        if db_user:
            return jsonify({"message": 'User Logged in Via Cookie', "user_id": db_user.id})
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
    app.run()
