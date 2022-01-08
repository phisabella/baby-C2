import json
import resources

from flask import Flask
from flask_restful import Api
from database.db import initialize_db

# Initialize our Flask app
app = Flask(__name__)

# Configure our database on localhost
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/server'
}

# Initialize our database
initialize_db(app)

# Initialize our API
api = Api(app)

# Define the routes for each of our resources
api.add_resource(resources.Tasks, '/tasks', endpoint='tasks')
api.add_resource(resources.Results, '/results')
api.add_resource(resources.History, '/history')

# Start the Flask app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
