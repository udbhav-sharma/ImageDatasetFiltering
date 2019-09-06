import os
from os.path import dirname, join, splitext, basename
import json

path = '/Users/udbhavsharma/Downloads/v1/'
newFilePath = '/Users/udbhavsharma/Downloads/image-filter/static/images'

total = 0

data = []
status = {}

# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        path = join(r, file)
        filename, file_extension = splitext(path)

        if basename(filename) == '.DS_Store':
            continue

        total += 1
        parent = basename(dirname(path))
        ancestor = basename(dirname(dirname(path)))
        id = "%0*d" % (4, total)
        newFile = "%s%s" % (id, file_extension)

        data.append({
            "id" : id,
            "name" : newFile,
            "category" : ancestor,
            "subcategory" : parent,
            "originalUrl" : "" 
        })
        status[id] = 1

        os.rename(path, join(newFilePath, newFile))

with open('ImageDetail.json', 'w') as outfile:
    json.dump(data, outfile)

with open('ImageStatus.json', 'w') as outfile:
    json.dump(status, outfile)
