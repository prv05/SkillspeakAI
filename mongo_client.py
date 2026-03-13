from flask_pymongo import PyMongo

# Initialize lazily and bind in app.py via mongo.init_app(app)
mongo = PyMongo()