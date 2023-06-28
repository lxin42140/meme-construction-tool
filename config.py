import os

'''
DIRS
'''
CURR_DIR = os.path.dirname(os.path.realpath(
    __file__)) + "/"    # Path of current dir

TEMPLATE_DIR = CURR_DIR + 'templates/'
PREPROCESSED_TEMPLATES_DIR = CURR_DIR + 'processed_templates/'
# SVG_TEXTS_DIR = CURR_DIR + 'svg_texts/'
TEMPLATE_RESULTS_DIR = CURR_DIR + 'output/'
LOGS_DIR = CURR_DIR + 'output/logs/'
SVG_PLACED_TEXT_DIR = CURR_DIR + 'output/svg/'
RESULTS_DIR = CURR_DIR + 'output/image/'
OCR_DIR = CURR_DIR + 'output/ocr/'

FONT_DIR = CURR_DIR + 'fonts/'
FONTS_DIR_MAPPING = {
    'Impact': FONT_DIR + 'impact/impact.ttf',
    'Gothic': FONT_DIR + 'gothic/gothica1/GothicA1-Black.ttf',
    'Comic Sans MS': FONT_DIR + 'comic-sans-ms/COMIC.TTF',
    'Lato': FONT_DIR + 'lato/Lato-Black.ttf',
    'Arial': FONT_DIR + 'arial/ARIAL.TTF',
    'Unifont': FONT_DIR + 'unifont-15.0.03.otf',
    'Times New Roman': FONT_DIR + 'Times New Roman/times new roman.ttf'
}

'''
files
'''
TEXT_COORDINATE_FILE = TEMPLATE_RESULTS_DIR + \
    'templates_with_text_coordinates.csv'
TEXT_FILE = TEMPLATE_RESULTS_DIR + 'templates_with_text.csv'
MEME_METADATA_FILE = TEMPLATE_RESULTS_DIR + "meme_metadata_template.csv"
PREPROCESS_SUCCESS_FILE = LOGS_DIR + "preprocess_success.txt"
PREPROCESS_FAIL_FILE = LOGS_DIR + "preprocess_failed.txt"
CHAT_LOG_FILE = LOGS_DIR + "chat_log.txt"
