import json
import os
from os.path import basename, dirname, join, splitext

dataset_path = "/Users/udbhavsharma/Documents/Academics/CSE - 524/dataset/v5/dataset.json"
user = "minh"

data = {}
with open(dataset_path) as json_file:
    data = json.load(json_file)

images = []
if user in data["status_map"]:
    for key, value in data["status_map"][user].items():
        if value == 2:
            images.append(data["images"][key])

images = sorted(images, key = lambda x: x["id"])

print("Total: {}".format(len(images)))
for image in images: 
    print("{}: {}".format("->".join(image["category"]), image["name"]))
