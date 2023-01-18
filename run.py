import os
import json
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sql_notes import get_notes, Note, session

app = Flask(__name__)


@app.route("/")
def index():
    data = get_notes()
    return render_template("index.html", page_title="Dashboard", notes=data)


@app.route("/addNote", methods=["GET", "POST"])
def addNote():
    if request.method == "POST":
        # Create records in our database
        new_note = Note(
            Title = request.form.get('title'),
            IsList = False,
            Content = [
                {
                    "checked": False,
                    "content": request.form.get('content')
                }
            ]
        )
        # Add each instance of our Note into the session
        session.add(new_note)
        session.commit()

    return render_template("addNote.html", page_title="Add new note", action="/addNote")


@app.route("/addList", methods=["GET", "POST"])
def addList():
    if request.method == "POST":
        # Create records in our database
        new_note = Note(
            Title = request.form.get('title'),
            IsList = True,
            Content = [
                {
                    "checked": False,
                    "content": request.form.get('content')
                }
            ]
        )
        # Add each instance of our Note into the session
        session.add(new_note)
        try:
            session.commit()
        except:
            session.rollback()
            errorMsg = "There was an error submitting this request. Please, try again."
            return render_template("addList.html", page_title="Add new list", action="/addList", message=errorMsg)

    return render_template("addList.html", page_title="Add new list", action="/addList")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP","0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True
        #debug must be turned off before deployment
    )
