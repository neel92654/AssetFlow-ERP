from flask import jsonify

def success_response(message="Operation successful", data=None, status_code=200):
    response = {
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    }
    return jsonify(response), status_code

def error_response(message="Validation failed", errors=None, status_code=400):
    response = {
        "success": False,
        "message": message,
    }
    if errors:
        response["errors"] = errors
    return jsonify(response), status_code
