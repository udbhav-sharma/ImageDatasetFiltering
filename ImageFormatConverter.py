import argparse
from os import listdir, remove, system
from os.path import join, normpath, splitext

ext_format = {
    '.png': 'png',
    '.gif': 'gif'
}

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Image Format Converter")
    parser.add_argument('--path', required=True)
    opt = parser.parse_args()

    path = normpath(opt.path)

    count = 0
    for f in listdir(path):
        name, ext = splitext(f)

        old_path = join(path, f)
        new_path = join(path, (name + ".jpg"))
        
        if ext in ['.png', '.gif']: 
            count += 1
            print("%s -> %s" % (old_path, new_path))

            system("sips -s format {} {} --out {}".format(ext_format[ext], old_path, new_path))

            remove(old_path)

    print("Total Images converted: %d" % (count))
            