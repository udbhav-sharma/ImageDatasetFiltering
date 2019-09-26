from apscheduler.schedulers.background import BackgroundScheduler

from db import(
    Dataset,
    DBClient,
    User,
)

from flask import (
    Flask, 
    redirect,
    render_template, 
    request,
    session,
    url_for,
)

from flask_api import (
    FlaskAPI, 
    status as http_status,
)

from flask_login import (
    current_user,
    logout_user,
)

import atexit
import flask_login
import logging
import os
import re
import time

app = FlaskAPI(__name__)
app.secret_key = os.urandom(24)

# Init LoginManager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

dbclient = DBClient()

''' Authentication '''

@login_manager.user_loader
def user_loader(id):
    return dbclient.get_user(id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', error = "")

    user = dbclient.get_user(request.form['userid'])

    if user != None and request.form['password'] == user.password:
        flask_login.login_user(user)
        if 'next_url' in session:
            return redirect(session['next_url'])
        else:
            return 'Please open the dataset page again'

    return render_template('login.html', error = "Invalid user id or password")

@app.route('/logout')
def logout():
    logout_user()
    return "Logged out successfully!!"

''' APP API Definitions '''

@app.route("/dataset/<d_name>")
def home(d_name):

    # Checking if user is authenticated
    if not current_user.is_authenticated:
        session['next_url'] = request.path
        return redirect(url_for('login'))

    # Rendering Home Page
    return render_template("index.html", dataset_name = d_name, user = current_user.id)

@app.route("/api/dataset/<d_name>/<int:index>", methods=['GET'])
def next(d_name, index):

    # Validating request params
    dataset = dbclient.get_dataset(d_name)
    if dataset == None:
        return "No dataset with name " + d_name + " found", http_status.HTTP_400_BAD_REQUEST
    
    # Getting the Image from Dataset
    index = max(1, index)
    img = dataset.get_nth_image(index)

    if img is None: return {"id": "<END>"}

    # Returning Image Copy
    img_dict = img.copy()
    img_dict['status'] = dataset.get_status(img_dict["id"], current_user.id)
    return img_dict
    
@app.route("/api/dataset/<d_name>/status/<id>/<int:val>", methods=['PUT'])
def updateStatus(d_name, id, val):

    # Validating request params
    dataset = dbclient.get_dataset(d_name)
    if dataset == None:
        return "No dataset with name " + d_name + " found", http_status.HTTP_400_BAD_REQUEST
    
    if not (val in [0, 1, 2]):
        return "Invalid val passed", http_status.HTTP_400_BAD_REQUEST

    # Updating image status for the user
    if dataset.update_status(id, val, current_user.id):
        return "", http_status.HTTP_204_NO_CONTENT
    else:
        return "Error in updating status", http_status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route("/api/dataset/<d_name>/export", methods=['POST'])
def export(d_name):

    # New Dataset name validation
    n_d_name = request.form["name"]
    pattern = re.compile('[^a-zA-Z0-9-_]+')
    n_d_name = pattern.sub('', n_d_name)
    if len(n_d_name) == 0:
        return "Invalid new dataset name", http_status.HTTP_400_BAD_REQUEST
    if dbclient.get_dataset(n_d_name) != None:
        return "Dataset " + n_d_name + " already exists", http_status.HTTP_400_BAD_REQUEST

    # Existing Dataset Name validation
    dataset = dbclient.get_dataset(d_name)
    if dataset == None:
        return "No dataset with name " + d_name + " found", http_status.HTTP_400_BAD_REQUEST

    dbclient.create_dataset_from(d_name, n_d_name, current_user.id)
    
    return n_d_name, http_status.HTTP_201_CREATED

def save():
    dbclient.flush_all_to_disk()
    logging.info("Data persisted to disk")

def cleanup():
    dbclient.flush_all_to_disk()
    scheduler.shutdown()

if __name__ == "__main__":

    logging.basicConfig()
    logging.root.setLevel(logging.INFO)

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=save, trigger="interval", seconds=300)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(cleanup)

    # app.run()
    app.run(host='0.0.0.0', port=8080)
