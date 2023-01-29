from app import app
from flask import jsonify, request
from helpers.db_helpers import *

@app.get("/api/words")
def get_words():
    params = request.args
    session_token = params.get("sessionToken")
    if session_token is None:
        return jsonify("Session token not found")
    user_session_data = run_query("SELECT user_id FROM user_session WHERE session_token=?",[session_token])
    user_id = user_session_data[0][0]
    all_word_groups = run_query("SELECT word_groups.id, words.id, words.word FROM word_groups RIGHT JOIN words ON words.group_id=word_groups.id WHERE word_groups.user_id=?", [user_id])
    resp = []
    for word in all_word_groups:
        words = {}
        words["groupId"] = word[0]
        words["wordId"] = word[1]
        words["word"] = word[2]
        resp.append(words)
    return jsonify(resp)

@app.post("/api/words")
def add_words():
    params = request.args
    data = request.json
    session_token = params.get("sessionToken")
    words_to_add = data.get("words")
    if session_token is None:
        return jsonify("Session token not found!")
    user_session_data = run_query("SELECT * FROM user_session WHERE session_token=?",[session_token])
    user_id = user_session_data[0][1]
    run_query("INSERT INTO word_groups (user_id) VALUES (?)",[user_id])
    group_data = run_query("SELECT * FROM word_groups WHERE user_id=?",[user_id])
    group_id = group_data[-1][0]
    for word in words_to_add:
        run_query("INSERT INTO words (word,group_id,user_id) VALUES (?,?,?)",[word,group_id,user_id])
    # Next step after adding word works properly => ...JOIN answers ON answers.word_id=words.id WHERE words.user_id=?",[user_id]
    return jsonify("Words added to your database")