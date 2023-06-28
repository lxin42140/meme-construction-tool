import os
import cv2 as cv
import easyocr
import pytesseract as pt
import pandas as pd
from langdetect import detect
import argparse
from config import OCR_DIR


def easyocr_lib(results, directory=''):
    ocr_lang_detect = {
        "en": "en",
        "ch_sim": "zh-cn",
        "ta": "ta",
        "ms": "ms"
    }

    for i in os.listdir(directory):
        if i.startswith('.'):
            continue

        results["filename"].append(i)

        # loop through each support lang to try which one can generate results
        extracted_text = False
        for la in ocr_lang_detect.keys():
            # get reader for specific language
            # for easy_ocr, they do not support multiple languages concurrently, hence we need a specific reader for each lang
            reader = easyocr.Reader([la], gpu=False)
            # get the extract text
            text = reader.readtext(directory + i)
            # concat words together from [([[14, 188], [148, 188], [148, 238], [14, 238]], '请你滚', 0.9725993526362473), ([[162, 188], [250, 188], [250, 238], [162, 238]], '谢谢', 0.9927909141324388)]
            text = ' '.join([item[1] for item in text])

            extracted_text = extract_and_lang_detect(
                ocr_lang_detect, la, results, text)

            if extracted_text:
                break

        if not extracted_text:
            results["extracted_text"].append("-")
            results["language"].append("-")

    return results


def pytesseract_lib(results, directory):
    # supported lang detect, refer to https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    # for supported languages, refer to https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html
    ocr_lang_detect = {
        "eng": "en",
        "chi_sim": "zh-cn",
        "tam": "ta",
        "msa": "ms"
    }

    for i in os.listdir(directory):
        if i.startswith('.'):
            continue

        results["filename"].append(i)
        img = cv.imread(directory + i)

        # loop through each support lang to try which one can generate results
        extracted_text = False
        for la in ocr_lang_detect.keys():
            # get the extract text
            text = str(pt.image_to_string(image=img, lang=la))

            extracted_text = extract_and_lang_detect(
                ocr_lang_detect, la, results, text)

            if extracted_text:
                break

        if not extracted_text:
            results["extracted_text"].append("-")
            results["language"].append("-")

    return results


def extract_and_lang_detect(ocr_detect_mapping, la, results, extracted_text) -> bool:
    '''
    1. detect the language of the extracted text
    2. compare the detected language with language used for extraction
    3. if they are same, return true
    '''

    # did not extract any text
    if extract_text is None or len(extracted_text) == 0:
        return False

    # detect the extracted lang
    detected_lang = detect(extracted_text)

    # check if it matches
    # sometimes the ocr will detect english chars from chinese text, hence this helps to ensure that correct lang is detected
    if ocr_detect_mapping[la] == detected_lang:
        results["extracted_text"].append(extracted_text)
        results["language"].append(la)
        return True
    else:
        print(
            "[INFO] extract_text - attempted ocr with lang <{}> but detected <{}>".format(la, detected_lang))
        return False


def extract_text(directory, ocr_option=1):
    # NOTE: using multiple OCR lib at once will throw error
    try:
        results = {
            "filename": [],
            "extracted_text": [],
            "language": []
        }

        if ocr_option == 1:
            results = pytesseract_lib(results, directory)
        elif ocr_option == 2:
            results = easyocr_lib(results, directory)
        else:
            raise Exception("Invalid ocr library selection")

        df = pd.DataFrame(results)
        df.to_csv(
            OCR_DIR + 'ocr_{}_results.csv'.format(ocr_option), index=False)
        print("[INFO] extract_text - success, results saved in {}/ocr_{}_results.csv".format(OCR_DIR, ocr_option))
        return None
    except Exception as e:
        print("[ERROR] extract_text - {}".format(e))
        return e


'''
Command line args
'''
parser = argparse.ArgumentParser("OCR Check Command")
parser.add_argument(
    "dir", help="A string to specify the directory containing images", type=str)
parser.add_argument(
    "ocr_lib", help="(1) tesseract-ocr. (2) easy-ocr.", type=int)

if __name__ == '__main__':
    args = parser.parse_args()
    extract_text(args.dir + "/", args.ocr_lib)

    # extract_text(CURR_DIR + "results/", 3)
