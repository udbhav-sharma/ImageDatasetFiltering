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

image_details = {}
image_status = {}
empty_image = {
    "id": "<END>"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/image/<int:index>", methods=['GET'])
def next(index):
    if index > len(image_details): 
        return empty_image

    static_details = image_details[index-1]

    img = {'status' : 0}
    for key, val in static_details.items(): img[key] = val
    if static_details["id"] in image_status: img['status'] = image_status[static_details["id"]]

    return img

@app.route("/updateStatus/<id>/<int:val>", methods=['PUT'])
def updateStatus(id, val):
    image_status[id] = val

    return "", http_status.HTTP_204_NO_CONTENT

@app.route("/export", methods=['POST'])
def export():
    dataset_name = time.strftime("%Y%m%d-%H%M%S")

    print("Creating dataset with name: " + dataset_name)

    # Creating dataset directory
    path = dirname(os.path.realpath(__file__))
    res = join(join(path, "static"), "images")
    dest = join(join(path, "dataset"), dataset_name)

    os.makedirs(dest)

    # Exporting data
    for image in image_details:
        if image["id"] in image_status and image_status[image["id"]] == 1:
            shutil.copy(join(res, image["name"]), dest)

    return dataset_name, http_status.HTTP_201_CREATED
    
def init():
    global image_details
    global image_status

    with open('data/ImageDetail.json') as json_file:
        image_details = json.load(json_file)
    
    with open('data/ImageStatus.json') as json_file:
        image_status = json.load(json_file)

def save():
    print("Image Status written to the file")
    with open('data/ImageStatus.json', 'w') as outfile:
        json.dump(image_status, outfile)

def cleanup():
    save()
    scheduler.shutdown()

if __name__ == "__main__":
    init()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=save, trigger="interval", seconds=60)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(cleanup)

    app.run()
