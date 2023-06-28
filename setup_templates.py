import os
import sys
from matplotlib import pyplot as plt
import pandas as pd
import cv2
import numpy as np
import argparse
from config import TEXT_COORDINATE_FILE, TEXT_FILE

plt.rcParams['backend'] = 'TkAgg'
plt.rcParams["figure.autolayout"] = True

'''
global
'''
coords = {}                               # Image box coordinates
curr = ''                                 # Name of the current image file
drawing = False                           # Flag if the user has drawn top-left corner
redraw_image = False                      # Flag if the image needs to be redrawn
ix, iy = -1, -1                           # Top-left corner coordinates
img = np.zeros((512, 700, 3), np.uint8)     # Current image
cache = []                                # Image cache for current image

""" Start Helper functions """


def drawPoint(cx, cy, radius=2, color=(0, 0, 255), thickness=2):
    global img
    cv2.circle(img, (cx, cy), radius, color, thickness)


def draw_rectangle(coord):
    global img
    t = int(img.shape[0]/100)
    drawPoint(coord[0], coord[1], thickness=t)
    drawPoint(coord[2], coord[3], thickness=t)
    cv2.rectangle(img, (coord[0], coord[1]),
                  (coord[2], coord[3]), (0, 255, 255), t)


def getXY(event, x, y, flags, param):

    global ix, iy, drawing, img, cache, coords, curr, redraw_image

    t = int(img.shape[0]/100)

    if event == cv2.EVENT_LBUTTONDOWN and drawing == False:        # If the user draws the top-left corner
        drawing = True
        ix = x
        iy = y
        drawPoint(x, y, thickness=t)

    elif event == cv2.EVENT_LBUTTONDOWN and drawing == True:       # If the user draws the bottom-right corner
        if ix >= x or iy >= y:
            print("[ERROR] setup: select top left corner first")
            redraw_image = True
        else:
            coords[curr].append((ix, iy, x, y))
            print("[INFO] setup: {}".format((ix, iy, x, y)))

        drawing = False
        ix, iy = -1, -1

    elif event == cv2.EVENT_RBUTTONDOWN:                             # Right-click on a box to erase it
        for i, coord in enumerate(coords[curr]):
            if x >= coord[0] and x <= coord[2] and y >= coord[1] and y <= coord[3]:
                del coords[curr][i]
                redraw_image = True
                break


""" End Helper functions """


def setup(directory=None):
    global img, cache, curr, redraw_image, coords

    template_text_coords = []

    # read existing coordinate file, if any
    try:
        # Parse csv file with the coordinates for the text
        template_text_coords = pd.read_csv(
            TEXT_COORDINATE_FILE, index_col='Unnamed: 0')
        template_text_coords = template_text_coords.T    # Transpose the data frame
        template_text_coords = template_text_coords.to_dict()     # Convert to dict
    except Exception as e:
        print(
            "[ERROR] setup: cannot read {}; {}".format(TEXT_COORDINATE_FILE, e))

    try:
        for i in os.listdir(directory):     # Loop through each image

            if i.startswith('.'):      # Skip if image name is not correct
                continue

            img = plt.imread(directory + '/' + i)           # Reading image
            # Converts the color space of the image from BGR (Blue-Green-Red) to RGB (Red-Green-Blue).
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Adding the original image to the cache
            cache = [img.copy()]
            # Extracting file name for storage
            curr = i.split('/')[-1]
            # Init the coordinate dictionary for current file
            coords[curr] = []

            if template_text_coords != []:     # Parse coord in csv file from ['[275, 1077, 1667, 1668]', '[293, 3206, 1674, 3809]']
                # [['275', ' 1077', ' 1667', ' 1668'], ['293', ' 3206', ' 1674', ' 3809']]
                temp = [x.strip()[1:-1].split(',')
                        for x in template_text_coords[curr].values()]
                # [[275, 1077, 1667, 1668], [293, 3206, 1674, 3809]]
                coords[curr] = [[int(y) for y in x] for x in temp]

            print("[INFO] setup: setting up for {}".format(curr))

            # Create a window and bind the function to window, the cv2.WINDOW_NORMAL flag allows the window to be resizable.
            cv2.namedWindow(curr, cv2.WINDOW_NORMAL)
            # cv2.WND_PROP_TOPMOST, which makes the window appear on top of other windows. The value 1 indicates that the property is set to true.
            cv2.setWindowProperty(curr, cv2.WND_PROP_TOPMOST, 1)
            # Connect the mouse button to our callback function getXY
            cv2.setMouseCallback(curr, getXY)

            while True:

                for coord in coords[curr]:    # loop through each coord in the list
                    draw_rectangle(coord)

                if len(coords) == 0 or redraw_image is True:
                    img = cache[-1].copy()     # restore latest image cache
                    redraw_image = False
                    print("[INFO] setup: redrawn image")

                cv2.imshow(curr, img)

                if cv2.waitKey(10) == 27 or cv2.waitKey(10) == ord('n'):
                    break

            cv2.destroyAllWindows()

        df = pd.DataFrame.from_dict(coords, orient='index').fillna(0)
        df.to_csv(TEXT_COORDINATE_FILE)
        print("[INFO] setup: templates processed successfully and coordinates stored in " +
              TEXT_COORDINATE_FILE)
    except Exception as e:
        print("[ERROR] setup: error={}".format(e))
        return e


'''
Command line args
'''
parser = argparse.ArgumentParser("Setup Command")
parser.add_argument(
    "dir", help="A string to specify the directory containing images", type=str)

if __name__ == '__main__':
    args = parser.parse_args()
    setup(args.dir + "/")
