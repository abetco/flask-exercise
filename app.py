from typing import Tuple

from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)


def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.
    
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)


# TODO: Implement the rest of the API here!
@app.route("/users", methods=["GET"])
def users():
    team = request.args.get("team")
    if not team:
        data = {"users": db.get("users")}
        return create_response(data)
    users = db.get("users")
    team_users = [u for u in users if u["team"] == team]
    data = {"users": team_users}
    return create_response(data)


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    user = db.getById("users", user_id)
    data = {"user": user}
    if user == None:
        return create_response(status=404, message="Invalid ID")
    return create_response(data)


@app.route("/users", methods=["POST"])
def create_user():
    body = request.get_json("user")
    user = db.create("users", body)
    if user == None:
        return create_response(status=404, message="User info not found")
    if "name" not in user or "age" not in user or "team" not in user:
        return create_response(status=422, message="Some information is missing!")
    return create_response({"user": user}, status=201)


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.getById("users", user_id)
    if user == None:
        return create_response(status=404, message="Invalid ID")
    db.deleteById("users", user_id)
    return create_response(message="Successfully deleted!")


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    update_values = request.get_json("user")
    user = db.getById("users", user_id)
    if user == None:
        return create_response(status=404, message="Invalid ID")
    db.updateById("users", user_id, update_values)
    return create_response({"user": user}, status=201)


"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(debug=True)
