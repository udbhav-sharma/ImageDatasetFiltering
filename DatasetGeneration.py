import argparse
import json
import os
from os.path import basename, dirname, join, splitext
import shutil

# This script is used to generate the dataset for the first time to get filtered.
# Takes Input Path for images directory and Output Path

parser = argparse.ArgumentParser(description="Generate dataset")
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
opt = parser.parse_args()

input_path = os.path.normpath(opt.input)
output_path = os.path.normpath(opt.output)

file_to_be_filtered = {".DS_Store"}

total = 0
data = {}

images_path = join(output_path, "images")

if not os.path.exists(images_path): os.makedirs(images_path)

for r, d, f in os.walk(input_path):
    for file in f:
        path = join(r, file)
        _, file_extension = splitext(path)

        # Skipping .DS_Store file
        if file in file_to_be_filtered: continue

        total += 1
        id = "%0*d" % (4, total)
        name = "%s%s" % (id, file_extension)
        category = []

        parent_path = dirname(path)
        while (input_path != parent_path):
            category.insert(0, basename(parent_path))
            parent_path = dirname(parent_path)

        data[id] = {
            "id" : id,
            "name" : name,
            "category" : category
        }

        shutil.copy(path, join(images_path, name))

with open(join(output_path, 'dataset.json'), 'w') as outfile:
    json.dump({
        "images": data,
        "status_map": {},
        "created_by": ""
    }, outfile)
