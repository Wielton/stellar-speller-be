from app import app
from flask import jsonify, request
from helpers.db_helpers import *

@app.get("/api/answers")
def get_answers():
    params = request.args
    session_token = params.get("sessionToken")
    user_session = run_query("SELECT * FROM user_session WHERE session_token=?",[session_token])
    user_id = user_session[0][1]
    # RIGHT JOIN answers ON answers.words_id=words.id
    all_answers_data = run_query("SELECT * FROM answers WHERE user_id=?", [user_id])
    print(all_answers_data)
    resp = []
    for answers in all_answers_data:
        answer = {}
        answer["word"] = answers[1]
        answer["ogWordId"] = answers[2]
        resp.append(answer)
    return jsonify(resp)


@app.post("/api/answers")
def add_answers():
    params = request.args
    session_token = params.get("sessionToken")
    user_session = run_query("SELECT * FROM user_session WHERE session_token=?",[session_token])
    user_id = user_session[0][1]
    data = request.json
    words_to_add = data.get("words")
    print(words_to_add)
    for words in words_to_add:
        print(words["word"])
        word = words["word"]
        words_id = words["wordId"]
        run_query("INSERT INTO answers (word,words_id, user_id) VALUES (?,?,?)",[word, words_id,user_id])
    # Next step after adding word works properly => ...JOIN answers ON answers.word_id=words.id WHERE words.user_id=?",[user_id]
    return jsonify("Answers added to the database")