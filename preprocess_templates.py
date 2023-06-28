import os
import cv2
import numpy as np
import argparse
from config import PREPROCESSED_TEMPLATES_DIR, PREPROCESS_SUCCESS_FILE, PREPROCESS_FAIL_FILE, LOGS_DIR
'''
const
'''
DEFAULT_OPTIONS = {
    'resize': 0,
    'grayscale': 0,
    'normalize': 0,
    'scale': 0
}


def preprocess(directory='', options=DEFAULT_OPTIONS):
    try:
        if directory == '' or directory is None:
            raise Exception("No directory selected")

        print("[INFO] preprocess: starting preprocess, dir = {}, options = {}".format(
            directory, options))

        # store the images that have been processed
        success_images = []
        failed_images = []

        for i in os.listdir(directory):
            if i.startswith('.'):
                continue

            try:
                img = cv2.imread(directory + '/' + i)           # Load image

                if len(options) <= 0:
                    raise Exception("No option selected")

                if options['resize'] == 1:     # Resize image
                    img = cv2.resize(img, (448, 448))

                if options['grayscale'] == 1:      # Convert image to grayscale
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                if options['normalize'] == 1:     # Normalize pixel values
                    img = img.astype('float32') / 255.0

                if options['scale'] == 1:     # Scale pixel values to 0-255 range
                    img = img * 255.0

                img = img.astype('uint8')       # Convert pixel values to uint8
                cv2.imwrite(PREPROCESSED_TEMPLATES_DIR +
                            i, img)       # Save image
                success_images.append(i)
            except Exception as e:
                print(
                    "[ERROR] preprocess: error processing image={}, error={}".format(i, e))
                failed_images.append(i)

        # output result to files
        export_preprocess_result(PREPROCESS_SUCCESS_FILE, success_images)
        export_preprocess_result(PREPROCESS_FAIL_FILE, failed_images)

        print("[INFO] preprocess: success")

    except Exception as e:
        print("[ERROR] preprocess: error={}".format(e))
        return e


def export_preprocess_result(file_name, images):
    if len(images) > 0:
        # delete old file
        try:
            os.remove(file_name)
        except:
            pass

        # create new file
        with open(file_name, 'w') as file:
            file.writelines(
                "%s\n" % image_name for image_name in images)

        print("[INFO] preprocess: log {} saved in {} dir".format(
            file_name, LOGS_DIR))


'''
Command line args
'''
parser = argparse.ArgumentParser("Preprocess Command")
parser.add_argument(
    "dir", help="A string to specify the directory containing images", type=str)
parser.add_argument(
    "--resize", help="A int to dictate if image should be resized to 448 by 448", type=int)
parser.add_argument(
    "--grayscale", help="A int to dictate if image should be gray scaled", type=int)
parser.add_argument(
    "--normalize", help="A int to dictate if image should be normalized", type=int)
parser.add_argument(
    "--scale", help="A int to dictate if image should be scaled", type=int)

if __name__ == '__main__':
    args = parser.parse_args()
    preprocess(args.dir + "/", {
        'resize': args.resize,
        'grayscale': args.grayscale,
        'normalize': args.normalize,
        'scale': args.scale
    })
