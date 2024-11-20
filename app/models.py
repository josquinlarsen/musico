from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(75), nullable=False, unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# Piece (music) model
class Piece(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    instrumentation = db.Column(db.String(180), nullable=False)
    duration = db.Column(db.String(50), nullable=True)
    