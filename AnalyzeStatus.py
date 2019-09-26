import argparse
import json
import os
from os.path import basename, dirname, join, splitext

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Analyze Status")
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--user', required=True)
    opt = parser.parse_args()

    path = join(os.path.normpath(opt.dataset), "dataset.json")
    user = os.path.normpath(opt.user)

    dataset = {}
    with open(path) as json_file:
        dataset = json.load(json_file)

    images = []
    if user in dataset["status_map"]:
        for key, value in dataset["status_map"][user].items():
            if value == 2:
                images.append(dataset["images"][key])

    images = sorted(images, key = lambda x: x["id"])

    print("Total: {}".format(len(images)))
    for image in images: 
        print("{}: {}".format("->".join(image["category"]), image["name"]))
