from os.path import (
    dirname, 
    join, 
    splitext,
)

import copy
import datetime
import flask_login
import json
import logging
import os
import shutil

class User(flask_login.UserMixin):

    def __init__(self, id, password):
        self.id = id
        self.password = password

class Dataset():

    def __init__(self, images = {}, status_map = {}, created_by = ""):
        self.images = images
        self.__image_ids = sorted(self.images.keys())
        self.status_map = status_map
        self.created_by = created_by

    def size(self):
        return len(self.__image_ids)

    def get_status(self, image_id, username):
        if username in self.status_map and image_id in self.status_map[username]:
            return self.status_map[username][image_id]

        return 1

    def update_status(self, image_id, val, username):
        if image_id in self.images:
            if username not in self.status_map:
                self.status_map[username] = {}

            self.status_map[username][image_id] = val

            return True

        return False

    def get_nth_image(self, index):
        if index > len(self.__image_ids): 
            return None

        return self.images[self.__image_ids[index-1]]

class DBClient():

    def __init__(self):
        self.__datasets = {}
        self.__users = self.load_users()
        self.__storage_path = join(join(dirname(os.path.realpath(__file__)), "static"), "dataset")
        logging.info("Storage path: %s" % self.__storage_path)

    def get_user(self, id):
        if id in self.__users:
            return User(id = id, password = self.__users[id]["password"])

        return None

    def get_dataset(self, d_name):

        if d_name not in self.__datasets:
            json_path = self.dataset_json(d_name)

            if os.path.exists(json_path):
                with open(json_path) as json_file:
                    json_data = json.load(json_file)
                    self.__datasets[d_name] = Dataset(\
                        images = json_data['images'],\
                        status_map = json_data['status_map'],\
                        created_by = json_data['created_by'])
            else:
                return None

        return self.__datasets[d_name]

    def create_dataset_from(self, d_name, n_d_name, username):

        dataset = self.get_dataset(d_name)
        src = self.dataset_images_dir(d_name)

        # Create New Dataset Dir
        dest = self.dataset_images_dir(n_d_name)
        os.makedirs(dest)

        new_images = {}
        count = 0
        str_len = len(str(dataset.size()))

        for key in sorted(dataset.images.keys()):
            image = dataset.images[key]

            if dataset.get_status(key, username) == 1:
                shutil.copy(join(src, image["name"]), dest)
                
                _, file_extension = splitext(image["name"])

                count += 1
                id = "%0*d" % (str_len, count)
                name = "%s%s" % (id, file_extension)
                category = copy.deepcopy(image["category"])

                os.rename(join(dest, image["name"]), join(dest, name))

                new_images[id] = {
                    "id" : id, 
                    "name" : name, 
                    "category" : category
                }

        new_dataset = Dataset(images = new_images, created_by = username)

        self.__datasets[n_d_name] = new_dataset     

    def flush_all_to_disk(self):
        for d_name, dataset in self.__datasets.items():
            with open(self.dataset_json(d_name), 'w') as outfile:
                json.dump({
                    "images" : dataset.images, 
                    "status_map" : dataset.status_map,
                    "created_by" : dataset.created_by
                    }, outfile, indent=4)

        logging.debug("%s dataset flushed to disk" % d_name)

    def dataset_json(self, d_name):
        return join(self.dataset_dir(d_name), "dataset.json")

    def dataset_images_dir(self, d_name):
        return join(self.dataset_dir(d_name), "images")

    def dataset_dir(self, d_name):
        return join(self.__storage_path, d_name)

    def load_users(self):
        if os.path.exists("users.json"):
            with open("users.json") as json_file:
                return json.load(json_file)

        return {}
