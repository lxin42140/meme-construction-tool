import os
import pandas as pd
import pygame as pg
from config import *
import tkinter as tk
import tkinter.ttk as ttk
import argparse

pg.init()  # init pygames
COLOR_INACTIVE = pg.Color('red')
COLOR_ACTIVE = pg.Color('green')
FONT = pg.font.Font(None, 23)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text.upper()
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        self.text = self.text.upper()

        # toggle the outline color of the selected input box
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False

            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        # capture user keyboard input
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, screen):
        # Blit the text on to screen
        self.blit_text(screen)
        # Blit the rect box on to screen
        pg.draw.rect(screen, self.color, self.rect, 2)

    def blit_text(self, screen):
        words = self.text.split(' ')
        space = FONT.size(' ')[0]  # The width of a space.
        word_height = FONT.size('A')[1]
        x, y = self.rect.x, self.rect.y

        for word in words:
            word_surface = FONT.render(word, True, self.color)
            word_width, wh = word_surface.get_size()

            if x + word_width >= self.rect.x + self.rect.w:
                x = self.rect.x     # Reset the x.
                y += word_height    # Start on new row.

            screen.blit(word_surface, (x+2, y+2+word_height))

            x += word_width + space


def input_text(directory=None):
    try:
        template_text_coords = pd.read_csv(
            TEXT_COORDINATE_FILE, index_col='Unnamed: 0').T.to_dict()

        all_texts = {}

        for i in os.listdir(directory):
            if i.startswith('.'):
                continue

            # Extracting name of image
            curr_image = i.split('/')[-1]
            # convert string coordinates for each image to [[244.0, 1400.0, 1811.0, 1947.0], [203.0, 3627.0, 1813.0, 4027.0]]
            # x = '(244, 1400, 1811, 1947)'
            coords = [[float(y.strip()) for y in x[1:-1].split(',') if y != '']
                      for x in template_text_coords[curr_image].values()]

            clock = pg.time.Clock()

            # input text loop
            # store text entered by user as
            '''
            { "2.img": [  
                ["text 1", "text 2"], 
                ["text 3", "text 4"]  
                ]
            }
            '''
            all_texts[curr_image] = []

            while True:
                '''
                Input text loop
                '''
                # reset
                done = False

                # load current template background to pygame
                bg = pg.image.load(directory + curr_image)

                # create pygame window
                screen = pg.display.set_mode(bg.get_size())

                # create input box for the current template
                input_boxes = []
                for i in coords:
                    input_boxes.append(
                        InputBox(i[0], i[1], i[2]-i[0], i[3]-i[1]))

                all_texts[curr_image].append([])
                curr_list = all_texts[curr_image][len(
                    all_texts[curr_image]) - 1]

                while not done:
                    #  draw the current_image onto the screen surface at the position (0, 0).
                    screen.blit(bg, (0, 0))

                    # capture user events
                    for event in pg.event.get():
                        # user close the current window
                        if event.type == pg.QUIT:
                            done = True

                        for box in input_boxes:
                            box.handle_event(event)

                    # draw entered text on screen
                    for box in input_boxes:
                        box.draw(screen)

                    if done:
                        for box in input_boxes:
                            # only append text if its not empty
                            if box.text is not None and len(box.text) > 0:
                                curr_list.append(box.text)

                    # updates the contents of the display window.
                    pg.display.flip()
                    # limit the frame rate to 30 frames per second (FPS).
                    clock.tick(30)

                '''
                selection loop
                '''
                window_size = bg.get_size()
                true_button = pg.Rect(100, 200, 100, 50)
                false_button = pg.Rect(250, 200, 100, 50)

                prompt_font = pg.font.Font(None, 30)
                prompt_text = prompt_font.render(
                    "Add another caption for template", True, (0, 0, 0))
                prompt_rect = prompt_text.get_rect(
                    center=(window_size[0] // 2, window_size[1] // 2))
                # Update prompt_rect position to be above the buttons
                prompt_rect.center = (
                    window_size[0] // 2, true_button.y - prompt_rect.height // 2)

                user_selection = None

                while user_selection is None:
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            pg.quit()
                        elif event.type == pg.MOUSEBUTTONDOWN:
                            mouse_pos = pg.mouse.get_pos()
                            if true_button.collidepoint(mouse_pos):
                                user_selection = False
                            elif false_button.collidepoint(mouse_pos):
                                user_selection = True

                    screen.blit(bg, (0, 0))  # Draw the background image

                    # Draw translucent gray overlay
                    overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
                    overlay.fill((128, 128, 128, 140))
                    screen.blit(overlay, (0, 0))

                    # Draw the buttons
                    pg.draw.rect(screen, (0, 255, 0), true_button)
                    pg.draw.rect(screen, (255, 0, 0), false_button)

                    # Draw the prompt text
                    screen.blit(prompt_text, prompt_rect)

                    # Add text to buttons
                    true_font = pg.font.Font(None, 30)
                    true_text = true_font.render("Yes", True, (255, 255, 255))
                    true_text_rect = true_text.get_rect(
                        center=true_button.center)
                    screen.blit(true_text, true_text_rect)

                    false_font = pg.font.Font(None, 30)
                    false_text = false_font.render("No", True, (255, 255, 255))
                    false_text_rect = false_text.get_rect(
                        center=false_button.center)
                    screen.blit(false_text, false_text_rect)

                    pg.display.flip()

                if user_selection:
                    break

        # process the captions and produce csv file with following format
        # file1,caption,caption
        # file1,caption2,caption2
        # file2,caption,caption
        df = pd.DataFrame(index=None)
        for file in all_texts.keys():
            captions = all_texts[file]
            captions = [[file] + text for text in captions]
            df = pd.concat([df, pd.DataFrame(data=captions, index=None)])

        # export as csv
        df.to_csv(TEXT_FILE, index=None)
        print("[INFO] text input: text stored in " + TEXT_FILE)
        pg.quit()
    except Exception as e:
        print("[ERROR] text input: error={}".format(e))
        return e


'''
Command line args
'''
parser = argparse.ArgumentParser("Text Input Command")
parser.add_argument(
    "dir", help="A string to specify the directory containing images", type=str)

if __name__ == '__main__':
    args = parser.parse_args()
    input_text(args.dir + "/")
    # input_text(PREPROCESSED_TEMPLATES_DIR)
