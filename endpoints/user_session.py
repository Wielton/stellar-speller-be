from app import app
from flask import jsonify, request
from helpers.db_helpers import *
import bcrypt
import uuid


# Bcrypt password encryption handling

def encrypt_password(password):
    salt = bcrypt.gensalt(rounds=5)
    hash_result = bcrypt.hashpw(password.encode(), salt)
    print(hash_result)
    decrypted_password = hash_result.decode()
    return decrypted_password



@app.post("/api/user-session")
def user_login():
    data = request.json
    username = data.get("username")
    password_input = data.get("password")
    
    user_info = run_query("SELECT * FROM users WHERE username=?",[username])
    if user_info is None:
        return jsonify("Username not found")
    
    user_id = user_info[0][0]
    user_username = user_info[0][1]
    user_password = user_info[0][2]
    print(user_id)
    if not bcrypt.checkpw(password_input.encode(), user_password.encode()):
        return jsonify("Password doesn't match, please try again"),401
    login_token = str(uuid.uuid4().hex)
    logged_in = run_query("SELECT * FROM user_session WHERE user_id=?",[user_id])
    if logged_in is None:
        run_query("INSERT INTO user_session (user_id,session_token) VALUES (?,?)", [user_id,login_token])
        print('Logged in now')
    else:
        # I could UPDATE here but I chose to delete then create a new session instance as I figured this is a better thing to do because of token lifecycles and other errors that could occur from just updating one column
        run_query("DELETE FROM user_session WHERE user_id=?",[user_id])
        run_query("INSERT INTO user_session (user_id, session_token) VALUES (?,?)", [user_id,login_token])
    user = {}
    user["userId"] = user_id
    user["username"] = user_username
    user["sessionToken"] = login_token
    return jsonify(user)


@app.delete("/api/user-session")
def user_logout():
    params = request.args
    session_token = params.get("sessionToken")
    if session_token is None:
        return jsonify("Session token not found")
    else:
        session = run_query("SELECT * FROM user_session WHERE session_token=?",[session_token])
        if session is not None:
            run_query("DELETE FROM user_session WHERE session_token=?",[session_token])
            return jsonify("User logged out"),204
        else:
            return jsonify("You're not logged in."), 404