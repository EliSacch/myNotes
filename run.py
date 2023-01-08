import os
import json
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    data = []
    with open("data/notes.json", "r") as json_data:
        data = json.load(json_data)
    return render_template("index.html", page_title="Dashboard", notes=data)

@app.route("/add")
def add():
    return render_template("add.html", page_title="Add new")
    

if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP","0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True
        #debug must be turned off before deployment
    )
