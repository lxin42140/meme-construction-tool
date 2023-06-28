import os
import time
from PIL import Image, ImageFont, ImageDraw
import pandas as pd
import svgwrite as svg
import textwrap
import warnings
import argparse
from config import *
from datetime import datetime

warnings.filterwarnings("ignore")

'''
const
'''
FONT_OPTIONS = {
    1: 'Impact',
    2: 'Gothic',
    3: 'Comic Sans MS',
    4: 'Lato',
    5: 'Arial',
    6: 'Unifont',
    7: 'Times New Roman'
}


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# def generateTextSVG(image_path, texts, coordinates, chosen_font):
#     '''
#     Generates separate SVG files for each text at (0, 0)
#     '''
#     for i in texts.keys():

#         dwg = svg.Drawing(SVG_TEXTS_DIR + image_path.split(".")
#                           [0].split("/")[-1] + '_text' + i + '.svg', (100, 100))

#         # add font type
#         dwg.embed_font(name=chosen_font,
#                        filename=FONTS_DIR_MAPPING[chosen_font])
#         dwg.embed_stylesheet(
#             ".font {{ font-family: {}; }}".format(chosen_font))
#         para = dwg.add(dwg.g(class_="font", ))

#         # process the box coord
#         box = [float(x.strip()) for x in coordinates[i][1:-1].split(',')]
#         # wrap
#         lines = textwrap.wrap(texts[str(i)],
#                               width=round(len(texts[str(i)])/3))
#         # scale text
#         _, font_size, size_per_line = wrap_and_scale_text(
#             box, lines, chosen_font)

#         # create main text ele
#         text = dwg.text(
#             text="",
#             insert=(0, 0),
#             stroke='none',
#             fill=svg.rgb(0, 0, 0, '%'),
#             font_size=font_size,
#         )

#         # Calculate the vertical position for each line
#         y_height = size_per_line[1]
#         y_position = 0

#         # Add each line as a <tspan> element within the <text> element
#         for line in lines:
#             tspan = dwg.tspan(line, x=[0], y=[y_position])
#             text.add(tspan)
#             y_position += y_height

#         para.add(text)

#         dwg.save()


def generateAllTextSVG(image_path, chosen_font, captions: list, coordinates):
    '''
    Generates a single SVG with all texts for an image at desired coordinates
    '''
    dwg = svg.Drawing(SVG_PLACED_TEXT_DIR + image_path.split(".")
                      [0].split("/")[-1] + '_placedTexts_{}.svg'.format(timestamp()))

    # add font type
    dwg.embed_font(name=chosen_font, filename=FONTS_DIR_MAPPING[chosen_font])
    dwg.embed_stylesheet(
        ".font {{ font-family: {}; width: 100%; height: 100%; }}".format(chosen_font))
    para = dwg.add(dwg.g(class_="font", ))

    for i, text in enumerate(captions):
        if not isinstance(text, str) or not isinstance(coordinates[str(i)], str):
            continue

        # process the box coord
        box = [float(x.strip()) for x in coordinates[str(i)][1:-1].split(',')]
        # wrap
        text = text.upper()
        lines = textwrap.wrap(text,
                              width=max(round(len(text)/3), 1))
        # scale text
        font, font_size, size_per_line = wrap_and_scale_text(
            box, lines, chosen_font)

        # create main text ele
        text = dwg.text(
            text="",
            insert=box,
            stroke='none',
            fill=svg.rgb(0, 0, 0, '%'),
            font_size=font_size,
        )

        # Calculate the vertical position for each line
        # line_width, line_height = size_per_line
        y_text = 0
        box_width = box[2] - box[0]
        # Add each line as a <tspan> element within the <text> element
        for line in lines:
            line_width, line_height = font.getsize(line)
            tspan = dwg.tspan(
                line, x=[box[0] + (box_width - line_width)/2], y=[box[1] + y_text])
            text.add(tspan)
            y_text += line_height

        para.add(text)

    dwg.save()


def imageOnText(image_path, chosen_font, captions: list, coordinates):
    '''
    Generates PNG file with meme template background and superimpose text
    For each set of caption associated with the template, we generate a separate imposed meme
    '''
    filename = RESULTS_DIR + \
        image_path.split(".")[0].split(
            "/")[-1] + '_result_{}.png'.format(timestamp())
    '''
    text = {'1': 'a', '2': 'a'}
    '''
    image = Image.open(image_path)
    image_editable = ImageDraw.Draw(image)

    for i, text in enumerate(captions):
        if not isinstance(text, str) or not isinstance(coordinates[str(i)], str):
            continue

        # convert coord to list of floats, from '[275, 1077, 1667, 1668]' to [275.0, 1077.0, 1667.0, 1668.0]
        box = [float(x.strip())
               for x in coordinates[str(i)][1:-1].split(',')]

        # Automatic font customization
        # x coord of bottom right minus x coord of top left to get the width of box
        box_width = box[2] - box[0]
        # convert text to uppercase, TODO: allow user to specify if it should be uppercase
        box_text = text.upper()
        # wrap text into multiple lines, width = number of lines / 3
        lines = textwrap.wrap(box_text, width=max(1, round(len(box_text)/3)))

        font, font_size, _ = wrap_and_scale_text(box, lines, chosen_font)

        stroke_width = font_size//20

        if stroke_width < 1:
            stroke_width = 1

        y_text = 0
        for line in lines:
            line_width, line_height = font.getsize(line)
            image_editable.text((box[0] + (box_width - line_width)/2, box[1] + y_text),      # xy: tuple[float, float], workaround to center align the text by adding padding to the x coord of top left point
                                line,           # text
                                (255,),     # fill
                                font,           # font
                                spacing=0,
                                align='center',
                                stroke_fill="#000",
                                stroke_width=stroke_width)
            y_text += line_height

    image.save(filename)


def wrap_and_scale_text(box, lines, chosen_font):

    font_size = 100
    size_per_line = None

    while (size_per_line is None or \
            # width of length of line greater than box width
            size_per_line[0] > box[2] - box[0] or \
            # height of length of line greater than height per line
            size_per_line[1] > ((box[3] - box[1])/len(lines))) and \
            font_size > 0:
        # reload the selected font with the specified font size
        font = ImageFont.truetype(FONTS_DIR_MAPPING[chosen_font],
                                  font_size)
        # update the size of reloaded font
        # find the max size among all the lines

        def find_max_tuple(tuples):
            max_product = float('-inf')  # Initialize with negative infinity
            max_tuple = None

            for tup in tuples:
                product = tup[0] * tup[1]
                if product > max_product:
                    max_product = product
                    max_tuple = tup

            return max_tuple

        size_per_line = find_max_tuple([font.getsize(line) for line in lines])

        # decrease the font size
        font_size -= 1

    return (font, font_size, size_per_line)


def generate_from_dir(folder_path, chosen_font, option):

    # Load the text to impose for image
    template_text = pd.read_csv(
        TEXT_FILE, index_col=0)
    # Load the coordinates for text box
    template_text_coords = pd.read_csv(
        TEXT_COORDINATE_FILE, index_col=0).T.to_dict()

    for i in os.listdir(folder_path):
        if i.startswith('.'):
            continue

        image_path = folder_path + '/' + i

        # filter rows that match the current file
        try:
            filtered_df = template_text.loc[[i]]
        except:
            continue

        # check size of df
        num_rows, num_columns = filtered_df.shape
        if num_rows == 0 or num_columns == 0:
            continue

        # Iterate through rows and combine values into a list
        for _, row in filtered_df.iterrows():
            combined_caption = list(row.values)

            if option == 1:
                imageOnText(image_path, chosen_font,
                            combined_caption, template_text_coords[i])
            elif option == 2:
                generateAllTextSVG(image_path, chosen_font,
                                   combined_caption, template_text_coords[i])
            # elif option == 3:
            #     generateTextSVG(
            #         image_path, template_text[i], template_text_coords[i], chosen_font)
            else:
                raise Exception("selected option is not supported")

        print('[INFO] generate - generated for ', i)


def generate_from_file(folder_path, chosen_font, option, file):

    df = pd.read_csv(file, index_col=0)

    for i in os.listdir(folder_path):
        if i.startswith('.'):
            continue

        image_path = folder_path + '/' + i

        # filter rows that match the current file
        try:
            filtered_df = df.loc[[i]]
        except:
            continue

        # check size of df
        num_rows, num_columns = filtered_df.shape
        if num_rows == 0 or num_columns == 0:
            continue

        # Iterate through rows and combine values into a list
        for _, row in filtered_df.iterrows():
            row_data = list(row.values)
            row_data = [(row_data[i], row_data[i+1])
                        for i in range(0, len(row_data) - 1, 2)]
            captions = []
            text_coord = {}

            for i, tuple in enumerate(row_data):
                text_coord[str(i)] = tuple[0]
                captions.append(tuple[1])

            '''
            convert the data into the following
            captions = ['this is text 2-1', 'this is text 2-1']
            text_coord = {'0': '[16, 112, 405, 203]',
                '1': '[18, 330, 398, 433]'}
            '''

            if option == 1:
                imageOnText(image_path, chosen_font,
                            captions, text_coord)
            elif option == 2:
                generateAllTextSVG(image_path, chosen_font,
                                   captions, text_coord)
            else:
                raise Exception("selected option is not supported")

            # NOTE: sleep for a second is necessary to prevent image from not being saved before proceeding to the next image
            time.sleep(1)

        print('[INFO] generate - generated for ', i)


def generate(directory, option, chosen_font, file=None):
    try:
        # Load the selected font
        ImageFont.truetype(FONTS_DIR_MAPPING[chosen_font], 23)
        print('\n------- Started with option {}-------\n'.format(option))
        start = time.time()

        if not file:
            generate_from_dir(directory, chosen_font, option)
        else:
            generate_from_file(directory, chosen_font, option, file)

        end = time.time()
        print('\n------- Completed -------\n')
        print('[INFO] generate - Total time taken = ', str(end - start), '\n')
    except Exception as e:
        print("[ERROR] preprocess: error={}".format(e))
        return e


def font_preview(chosen_font):
    try:
        font_path = FONTS_DIR_MAPPING[chosen_font]
        text = "The quick brown fox jumps over the lazy dog"
        font_size = 20

        # Create a new image with a white background
        image_width = 900
        image_height = 200
        image = Image.new("RGB", (image_width, image_height), "white")
        draw = ImageDraw.Draw(image)

        # Load the font
        font = ImageFont.truetype(font_path, font_size)

        # Calculate the text position
        text_width, text_height = draw.textsize(text, font)
        text_x = (image_width - text_width) // 2
        text_y = (image_height - text_height) // 2

        # Draw the text on the image
        draw.text((text_x, text_y), text, font=font, fill="black")

        # Show the preview
        image.show()

    except Exception as e:
        print("[ERROR] font preview: error={}".format(e))
        return e


'''
Command line args
'''
parser = argparse.ArgumentParser("Meme Generation Command")
parser.add_argument(
    "dir", help="A string to specify the directory containing images", type=str)
# parser.add_argument(
#     "option", help="(1) Store SVG texts separately. (2) Store all SVG texts for an image at their coordinate positions. (3) Store image background + overlay text in SVG format", type=int)
parser.add_argument(
    "option", help="(1) Overlay text on template (with background, png format) (2) Place text for each template at coordinate positions (no background, SVG format)", type=int)
parser.add_argument(
    "font", help="(1) Impact. (2) Gothic. (3) Comic Sans MS. (4) Lato. (5) Arial. (6) Unifont. (7) Times New Roman", type=int)
parser.add_argument(
    "--csv_file", help="A string to specify the csv file path containing meme metadata", type=str)

if __name__ == '__main__':
    args = parser.parse_args()
    generate(CURR_DIR + args.dir + "/",
             args.option, FONT_OPTIONS[args.font], CURR_DIR + args.csv_file)
    # generate(PREPROCESSED_TEMPLATES_DIR, 2,
    #          FONT_OPTIONS[2], MEME_METADATA_FILE)
