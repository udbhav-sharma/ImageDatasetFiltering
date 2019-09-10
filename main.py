from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request
from flask_api import FlaskAPI, status as http_status
from os.path import dirname, join

import atexit
import json
import os
import shutil
import time

app = FlaskAPI(__name__)

datasets = {}
empty_image = {
    "id": "<END>"
}

@app.route("/dataset/<d_name>")
def home(d_name):
    load(d_name)

    return render_template("index.html", dataset_name = d_name)

@app.route("/dataset/<d_name>/<int:index>", methods=['GET'])
def next(d_name, index):
    load(d_name)

    if index > len(datasets[d_name]): 
        return empty_image

    # TODO: Optimize the retrieval
    key = sorted(datasets[d_name])[index-1]
    return datasets[d_name][key]

@app.route("/dataset/<d_name>/status/<id>/<int:val>", methods=['PUT'])
def updateStatus(d_name, id, val):
    load(d_name)

    if id in datasets[d_name]:
        datasets[d_name][id]["status"] = val
        return "", http_status.HTTP_204_NO_CONTENT
    else:
        return "Invalid dataset or image", http_status.HTTP_400_BAD_REQUEST

@app.route("/dataset/<d_name>/export", methods=['POST'])
def export(d_name):
    load(d_name)

    n_d_name =  request.form["name"]
    print("Creating dataset with name: " + n_d_name)

    if len(datasets[d_name]) == 0:
        return "Invalid dataset name", http_status.HTTP_400_BAD_REQUEST

    dest = images_dir(n_d_name)
    if os.path.exists(dest): return "Dataset already exists", http_status.HTTP_400_BAD_REQUEST
    
    os.makedirs(dest)

    src = images_dir(d_name)

    images_detail = {}
    # Exporting data
    for image in datasets[d_name].values():
        if image["status"] == 1:
            shutil.copy(join(src, image["name"]), dest)
            images_detail[image["id"]] = image
    
    with open(join(dataset_dir(n_d_name), 'ImagesDetail.json'), 'w') as outfile:
        json.dump(images_detail, outfile)

    return n_d_name, http_status.HTTP_201_CREATED

def load(d_name):
    global datasets

    if d_name not in datasets:
        images_detail_path = join(join(dataset_dir(), d_name), "ImagesDetail.json")

        if os.path.exists(images_detail_path):
            with open(images_detail_path) as json_file:
                datasets[d_name] = json.load(json_file)
        else:
            datasets[d_name] = {}

def save():
    for d_name in datasets:
        if len(datasets[d_name]) > 0:
            with open(join(dataset_dir(d_name), 'ImagesDetail.json'), 'w') as outfile:
                json.dump(datasets[d_name], outfile)

    print("Image Status written to the file")

def images_dir(d_name):
    return join(dataset_dir(d_name), "images")

def dataset_dir(d_name=None):
    if d_name is None:
        return join(static_dir(), "dataset")
    
    return join(dataset_dir(), d_name)

def static_dir(): 
    return join(main_dir(), "static")

def main_dir():
    return dirname(os.path.realpath(__file__))

def cleanup():
    save()
    scheduler.shutdown()

if __name__ == "__main__":

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=save, trigger="interval", seconds=60)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(cleanup)

    # app.run()
    app.run(host='0.0.0.0')
