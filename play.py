



# # app.py

# from flask import Flask, jsonify, request
# from flask_pymongo import PyMongo
# from flask_bcrypt import Bcrypt

# app = Flask(__name__)
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/inventory'
# app.config['BCRYPT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
# mongo = PyMongo(app)
# bcrypt = Bcrypt(app)

# # User Schema
# user_schema = {
#     'username': {'type': 'string', 'required': True, 'unique': True},
#     'email': {'type': 'string', 'required': True, 'unique': True},
#     'password': {'type': 'string', 'required': True, 'minlength': 6},
# }

# # Routes
# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()

#     # Validate data against the user schema
#     errors = validate_data(data, user_schema)
#     if errors:
#         return jsonify({'errors': errors}), 400

#     # Hash the password before saving it to the database
#     data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')

#     # Insert the user data into the database
#     user_id = mongo.db.users.insert_one(data).inserted_id

#     return jsonify({'user_id': str(user_id)}), 201

# def validate_data(data, schema):
#     errors = []
#     for field, field_schema in schema.items():
#         if field_schema.get('required') and field not in data:
#             errors.append(f"{field} is required.")
#         elif field_schema.get('type') == 'string' and not isinstance(data.get(field), str):
#             errors.append(f"{field} must be a string.")
#         elif field_schema.get('type') == 'number' and not isinstance(data.get(field), (int, float)):
#             errors.append(f"{field} must be a number.")
#         elif field_schema.get('minlength') and len(data.get(field, '')) < field_schema['minlength']:
#             errors.append(f"{field} must have a minimum length of {field_schema['minlength']} characters.")
#         elif field_schema.get('unique') and mongo.db.users.find_one({field: data[field]}):
#             errors.append(f"{field} already exists.")
#     return errors

# if __name__ == '__main__':
#     app.run(debug=True)



# app.py

# from flask import Flask, jsonify, request
# from flask_pymongo import PyMongo

# app = Flask(__name__)
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/inventory'
# mongo = PyMongo(app)

# # Business Schema
# business_schema = {
#     'business_name': {'type': 'string', 'required': True},
#     'email': {'type': 'string', 'required': True},
#     'location': {'type': 'string', 'required': True},
#     'phone': {'type': 'string', 'required': True},
#     'country': {'type': 'string', 'required': True},
# }

# # Routes
# @app.route('/add_business', methods=['POST'])
# def add_business():
#     data = request.get_json()

#     # Validate data against the business schema
#     errors = validate_data(data, business_schema)
#     if errors:
#         return jsonify({'errors': errors}), 400

#     # Insert the business data into the database
#     business_id = mongo.db.businesses.insert_one(data).inserted_id

#     return jsonify({'business_id': str(business_id)}), 201

# def validate_data(data, schema):
#     errors = []
#     for field, field_schema in schema.items():
#         if field_schema.get('required') and field not in data:
#             errors.append(f"{field} is required.")
#         elif field_schema.get('type') == 'string' and not isinstance(data.get(field), str):
#             errors.append(f"{field} must be a string.")
#     return errors

# if __name__ == '__main__':
#     app.run(debug=True)



# app.py

# from flask import Flask, jsonify, request
# # from flask_pymongo import PyMongo
# from pymongo import MongoClient
# from cerberus import Validator  # Use Cerberus for schema validation

# app = Flask(__name__)
# mongo = MongoClient('mongodb://localhost:27017/')

# # Business Schema
# business_schema = {
#     'business_name': {'type': 'string', 'required': True},
#     'email': {'type': 'string', 'required': True, 'regex': r'\S+@\S+\.\S+'},  # Example email validation
#     'location': {'type': 'string', 'required': True},
#     'phone': {'type': 'string', 'required': True, 'regex': r'^\+\d{1,15}$'},  # Example phone number validation
#     'country': {'type': 'string', 'required': True},
# }

# v = Validator(business_schema)

# # Routes
# @app.route('/add_business', methods=['POST'])
# def add_business():
#     data = request.get_json()

#     # Validate data against the business schema
#     if not v.validate(data):
#         return jsonify({'errors': v.errors}), 400

#     # Insert the business data into the database
#     business_id = mongo.inventory.businesses.insert_one(data).inserted_id

#     return jsonify({'business_id': str(business_id)}), 201

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
mongo = MongoClient('mongodb://localhost:27017/')

# Category Schema
category_schema = {
    'name': {'type': 'string', 'required': True},
    'business_id': {'type': 'reference', 'required': True, 'collection': 'business'},
    'quantity_of_items': {'type': 'integer', 'default': 0},
    'number_of_items_sold': {'type': 'integer', 'default': 0},
}

# Batch Schema
batch_schema = {
    'number_of_items_added': {'type': 'integer'},
    'total_items': {'type': 'integer'},
    'price': {'type': 'float'},
    'added_by': {'type': 'string'},
}

@app.route("/add", methods=["POST"])
def create_items():
    data  =  request.get_json()
    validate_data(data, category_schema)

    mongo.db.category.insert_one(data).inserted_id
    return jsonify({"message": "successfully"})


    

# Update Category with Batch Endpoint
@app.route('/update_category_with_batch/<category_id>', methods=['POST'])
def update_category_with_batch(category_id):
    try:
        category_data = request.get_json()

        # Validate the category data against the schema
        validate_data(category_data, category_schema)

        # Extract batch data from category_data
        batch_data = category_data.pop('batch', {})

        # Update the category
        mongo.db.category.update_one({'_id': ObjectId(category_id)}, {'$push': category_data})

        # Update the associated batch
        if batch_data:
            mongo.batch.update_one({'category_id': ObjectId(category_id)}, {'$push': batch_data}, upsert=True)

        return jsonify({'message': 'Category updated successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def validate_data(data, schema):
    pass



if __name__ == "__main__":
    app.run(debug=True)