from app import app
from flask import jsonify, request
from helpers.db_helpers import *

@app.get("/api/answers")
def get_answers():
    params = request.args
    session_token = params.get("sessionToken")
    if session_token is None:
        return jsonify("Session token not found")
    user_session_data = run_query("SELECT user_id FROM user_session WHERE session_token=?",[session_token])
    user_id = user_session_data[0][0]
    # RIGHT JOIN answers ON answers.words_id=words.id
    all_words_data = run_query("SELECT * FROM words WHERE user_id=?", [user_id])
    print(all_words_data)
    resp = []
    for word in all_words_data:
        answers = {}
        answers["word"] = word[1]
        answers["ogWordId"] = word[2]
        resp.append(resp)
    return jsonify(resp)

@app.post("/api/answers")
def add_answers():
    data = request.json
    words_to_add = data.get("words")
    print(words_to_add)
    for words in words_to_add:
        print(words["word"])
        word = words["word"]
        words_id = words["wordId"]
        run_query("INSERT INTO answers (word,words_id) VALUES (?,?)",[word, words_id])
    # Next step after adding word works properly => ...JOIN answers ON answers.word_id=words.id WHERE words.user_id=?",[user_id]
    return jsonify("Answers added to the database")