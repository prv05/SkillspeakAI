from flask_pymongo import PyMongo
from flask import Flask
from config import MONGO_URI

app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app) 