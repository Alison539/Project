from flask import Blueprint, jsonify, request

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/qec_data', methods=['POST'])
def process_data():
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    return jsonify({"received": data})