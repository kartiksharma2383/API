from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)                                            # Creates a Flask application instance, where __name__ tells Flask where your app is located.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'      # Configures the database URI for SQLAlchemy, using SQLite in this case.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False             # Disables the modification tracking feature of SQLAlchemy, which can save memory and improve performance.

db = SQLAlchemy(app)

# Model
class Drink(db.Model):                                                # Defines a model class named Drink that inherits from db.Model, which is the base class for all models in SQLAlchemy. 
    id = db.Column(db.Integer, primary_key=True)                      # Defines an id column that is an integer and serves as the primary key for the table.
    name = db.Column(db.String(80), unique=True, nullable=False)      # Defines a name column that is a string with a maximum length of 80 characters, must be unique, and cannot be null.
    description = db.Column(db.String(120))                           # Defines a description column that is a string with a maximum length of 120 characters.

    def to_dict(self):                                                # Defines a method to_dict that converts the Drink object into a dictionary format, which is useful for JSON serialization when sending responses from the API.
        return {
            "id": self.id,                                           
            "name": self.name,
            "description": self.description
        }

# Create tables
with app.app_context():                    # Creates an application context, which is necessary for certain operations in Flask, such as interacting with the database.                
    db.create_all()                        # Creates all the tables defined by the models in the database. In this case, it will create a table for the Drink model if it doesn't already exist.

# Home route
@app.route('/', methods=['GET'])                                     # Defines a route for the home page of the API, which responds to GET requests.
def home():                                                
    return jsonify({"message": "REST API is working"}), 200          # Returns a JSON response with a message indicating that the REST API is working, along with an HTTP status code of 200 (OK). 

# GET all drinks
@app.route('/drinks', methods=['GET'])                               # Defines a route for retrieving all drinks, which responds to GET requests.
def get_drinks():                                                    # Queries the database for all Drink records, converts each drink to a dictionary using the to_dict method, and returns a JSON response containing a list of all drinks, along with an HTTP status code of 200 (OK).
    drinks = Drink.query.all()                                       # Retrieves all records from the Drink table in the database and stores them in the variable drinks.
    return jsonify([drink.to_dict() for drink in drinks]), 200       # Uses a list comprehension to convert each Drink object in the drinks list to a dictionary using the to_dict method, and then returns a JSON response containing the list of drink dictionaries, along with an HTTP status code of 200 (OK).

# GET single drink by ID
@app.route('/drinks/<int:id>', methods=['GET'])                      # Defines a route for retrieving a single drink by its ID, which responds to GET requests. The <int:id> part of the route indicates that the ID will be passed as an integer parameter in the URL.
def get_drink(id):                                                   # Queries the database for a Drink record with the specified ID. If the drink is found, it converts it to a dictionary and returns it as a JSON response with an HTTP status code of 200 (OK). If the drink is not found, it returns a 404 error.
    drink = Drink.query.get_or_404(id)                               # Retrieves a Drink record from the database with the specified ID. If no record is found, it automatically returns a 404 error response.
    return jsonify(drink.to_dict()), 200                             # Converts the retrieved Drink object to a dictionary using the to_dict method and returns it as a JSON response, along with an HTTP status code of 200 (OK).

# POST (Create)
@app.route('/drinks', methods=['POST'])                              # Defines a route for creating a new drink, which responds to POST requests. This route expects a JSON payload containing the name and optionally the description of the drink.
def add_drink():                                                     # Retrieves the JSON data from the request, validates that the name is provided, and then creates a new Drink record in the database. If the drink is successfully created, it returns the new drink as a JSON response with an HTTP status code of 201 (Created).
    data = request.get_json()                                        # Retrieves the JSON data sent in the request body and stores it in the variable data.

    if not data or not data.get("name"):                             # Checks if the data is empty or if the "name" field is missing in the JSON payload. If either condition is true, it returns a JSON response with an error message indicating that the name is required, along with an HTTP status code of 400 (Bad Request).
        return jsonify({"error": "Name is required"}), 400          

    new_drink = Drink(                                               # Creates a new instance of the Drink model using the name and description from the JSON data. The name is required, while the description is optional.
        name=data["name"],                                           # Sets the name of the new drink to the value provided in the JSON payload under the "name" key.
        description=data.get("description")                          # Sets the description of the new drink to the value provided in the JSON payload under the "description" key, or None if it is not provided.
    )

    try:                                                             # Attempts to add the new drink to the database session and commit the transaction.
        db.session.add(new_drink)                                    # Adds the new drink instance to the current database session, marking it for insertion into the database.
        db.session.commit()                                          # Commits the current transaction, which saves the new drink to the database. 
        return jsonify(new_drink.to_dict()), 201                     # Converts the new drink instance to a dictionary using the to_dict method and returns it as a JSON response, along with an HTTP status code of 201 (Created).

    except IntegrityError:                                           # Catches any IntegrityError exceptions that occur during the database commit, which can happen if there is a violation of database constraints (such as a duplicate name).
        db.session.rollback()                                        # Rolls back the current transaction to undo any changes made to the database session, ensuring that the database remains in a consistent state after the error.
        return jsonify({"error": "Drink already exists"}), 400       # Returns a JSON response with an error message indicating that a drink with the same name already exists, along with an HTTP status code of 400 (Bad Request). 

# PUT (Update)
@app.route('/drinks/<int:id>', methods=['PUT'])                      # Defines a route for updating an existing drink by its ID, which responds to PUT requests. The <int:id> part of the route indicates that the ID will be passed as an integer parameter in the URL.
def update_drink(id):                                                # Retrieves the existing Drink record from the database using the provided ID. If the drink is found, it updates the name and description based on the JSON data sent in the request body. It then attempts to commit the changes to the database. If the update is successful, it returns the updated drink as a JSON response with an HTTP status code of 200 (OK).
    drink = Drink.query.get_or_404(id)                               # If no record is found, it automatically returns a 404 error response.
    data = request.get_json()                                        # Retrieves the JSON data sent in the request body and stores it in the variable data. 

    if not data or not data.get("name"):                             # Checks if the data is empty or if the "name" field is missing in the JSON payload. If either condition is true, it returns a JSON response with an error message indicating that the name is required, along with an HTTP status code of 400 (Bad Request).
        return jsonify({"error": "Name is required"}), 400           # Updates the name and description of the existing drink based on the values provided in the JSON payload. The name is required, while the description is optional.

    drink.name = data["name"]                                        # Sets the name of the existing drink to the value provided in the JSON payload under the "name" key.
    drink.description = data.get("description")                      # Sets the description of the existing drink to the value provided in the JSON payload under the "description" key, or None if it is not provided.

    try:                                                             # Attempts to commit the changes to the database.
        db.session.commit()                                          # Commits the current transaction, which saves the updated drink to the database. 
        return jsonify(drink.to_dict()), 200                         # Converts the updated drink instance to a dictionary using the to_dict method and returns it as a JSON response, along with an HTTP status code of 200 (OK).

    except IntegrityError:                                                            # Catches any IntegrityError exceptions that occur during the database commit, which can happen if there is a violation of database constraints (such as a duplicate name).
        db.session.rollback()                                                         # Rolls back the current transaction to undo any changes made to the database session, ensuring that the database remains in a consistent state after the error.
        return jsonify({"error": "Drink with this name already exists"}), 400         # Returns a JSON response with an error message indicating that a drink with the same name already exists, along with an HTTP status code of 400 (Bad Request).

# DELETE
@app.route('/drinks/<int:id>', methods=['DELETE'])                                    # Defines a route for deleting an existing drink by its ID, which responds to DELETE requests. The <int:id> part of the route indicates that the ID will be passed as an integer parameter in the URL.                    
def delete_drink(id):                                                                 # Retrieves the existing Drink record from the database using the provided ID. If the drink is found, it deletes the record from the database and commits the transaction. It then returns a JSON response with a success message and an HTTP status code of 200 (OK).
    drink = Drink.query.get_or_404(id)                                                # If no record is found, it automatically returns a 404 error response.
    db.session.delete(drink)                                                          # Marks the retrieved drink instance for deletion from the database.
    db.session.commit()                                                               # Commits the current transaction, which deletes the drink from the database.
    return jsonify({"message": "Drink deleted successfully"}), 200                    # Returns a JSON response with a message indicating that the drink was deleted successfully, along with an HTTP status code of 200 (OK).

# Run app
if __name__ == '__main__':                      # Checks if the script is being run directly (as the main program) rather than imported as a module. If this condition is true, it executes the code block that follows.
    app.run(debug = True)                       # Starts the Flask development server with debug mode enabled, which provides detailed error messages and auto-reloads the server when code changes are detected. 