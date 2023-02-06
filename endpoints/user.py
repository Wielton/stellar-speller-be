# This is the manager endpoint for signing up, getting and
#  patching info, and deleting account

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

# Response Codes: 
#   1. 200 = Success manager creation
#   2. 204 = success with No Content, which would be if nothing was edited in the user profile

# Error Codes: 
#   1. 401 = Access Denied because of lack of valid session token
#   2. 422 = Unprocessable because of lacking required info from manager 
#   3. 500 = Internal Server Error


@app.get("/api/user")
def get_user_info():
    params = request.args
    session_token = params.get("sessionToken")
    if session_token is None:
        return jsonify("Session token not found")
    
    user_session_data = run_query("SELECT user_id FROM user_session WHERE session_token=?",[session_token])
    user_id = user_session_data[0][0]
    user_data = run_query("SELECT * FROM users WHERE id=?", [user_id])
    user = {}
    user["userId"] = user_id
    user["username"] = user_data[0][1]
    return jsonify(user)
    



@app.post('/api/user')
def user_register():
    data = request.json
    username = data.get('username')
    password_input = data.get('password')
    if username is None:
        return jsonify("Username required"), 422
    if password_input is None:
        return jsonify("Password required"), 422
    encrypted_password = encrypt_password(password_input)
    run_query("INSERT INTO users (username, password) VALUES (?,?)", [ username, encrypted_password ])
    
    # Use cursor.lastRow() instead of using a SELECT query
    user_data = run_query("SELECT * FROM users WHERE username=?", [username])
    
    # Save user_id and session_token for INSERT and resp{}
    user_id = user_data[0][0]
    session_token = str(uuid.uuid4().hex)
    
    # INSERT session_token into user_session
    run_query("INSERT INTO user_session (user_id,session_token) VALUES (?,?)", [user_id,session_token])
    
    # Construct a resp object where each element of the Dict is set as a user{object}
    user = {}
    user['userId'] = user_id
    user['username'] = username
    user['sessionToken'] = session_token
    return jsonify(user)
# Manager redirected to logged-in where they see  


@app.patch('/api/manager')
def edit_profile():
    # GET params for session check
    params = request.args
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 401
    manager_info = run_query("SELECT * FROM manager JOIN manager_session ON manager_session.manager_id=manager.id WHERE token=?",[session_token])
    if manager_info is not None:
        manager_id = manager_info[0][0]
        data = request.json
        build_statement = ""
        # string join
        build_vals = []
        if data.get('username'):
            new_username = data.get('username')
            build_vals.append(new_username)
            build_statement+="username=?"
        else:
            pass
        if data.get('password'):
            new_password_input = data.get('password')
            new_password = encrypt_password(new_password_input)
            build_vals.append(new_password)
            if ("username" in build_statement):
                build_statement+=",password=?"
            else:
                build_statement+="password=?"
        else:
            pass
        if data.get('firstName'):
            new_first_name = data.get('firstName')
            build_vals.append(new_first_name)
            if ("username" in build_statement) or ("password" in build_statement):
                build_statement+=",first_name=?"
            else:
                build_statement+="first_name=?"
        else:
            pass
        if data.get('lastName'):
            new_last_name = data.get('lastName')
            build_vals.append(new_last_name)
            if ("username" in build_statement) or ("password" in build_statement) or ("first_name" in build_statement):
                build_statement+=",last_name=?"
            else:
                build_statement+="last_name=?"
        else:
            pass
        build_vals.append(manager_id)
        statement = str(build_statement)
        run_query("UPDATE manager SET "+statement+" WHERE id=?", build_vals)
        # Create error(500) for the server time out, or another server issue during the update process
        return jsonify("Your info was successfully edited"), 204
    else:
        return jsonify("Session not found"), 500

@app.delete('/api/manager')
def delete_account():
    params = request.args
    session_token = params.get('token')
    if not session_token:
        return jsonify("Session token not found!"), 401
    session = run_query("SELECT * FROM manager_session WHERE token=?",[session_token])
    if session is not None:
        user_id = session[0][3]
        run_query("DELETE FROM manager_session WHERE token=?",[session_token])
        run_query("DELETE FROM manager WHERE id=?",[user_id])
        return jsonify("Account deleted"), 204
    else:
        return jsonify("You must be logged in to delete your account"), 500