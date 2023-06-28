import os
import tkinter
from tkinter import filedialog, ttk, LEFT
import customtkinter
import preprocess_templates
import meme_generator
import setup_templates
import ocr_check
from config import *
import subprocess
from image_box_drawer import ImageBoxDrawer
import pandas as pd
from chat_tool import ChatWindow
import threading

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("Light")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("dark-blue")
customtkinter.set_widget_scaling(1)


class MessageBox(customtkinter.CTkToplevel):
    def __init__(self, message=''):
        super().__init__()
        self.geometry("400x150")
        self.title('Alert')
        self.label = customtkinter.CTkLabel(self, text=message)
        self.label.pack(padx=20, pady=20)
        self.button = customtkinter.CTkButton(
            self, text='OK!', command=self.destroy)
        self.button.pack(padx=20, pady=20)


class App(customtkinter.CTk):

    def __init__(self):

        super().__init__()

        # Operational variables
        # General
        self.selected_dir = ""
        self.out_dir = RESULTS_DIR

        # Configure window
        self.title("Meme Generator")
        self.geometry(f"{1200}x{800}")

        # Grid layout configuration (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Sidebar
        sidebar_frame = customtkinter.CTkFrame(
            self, width=140, corner_radius=0)
        sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
        # sidebar_frame.grid_rowconfigure(7, weight=1)

        # dir selection
        customtkinter.CTkLabel(
            sidebar_frame, text="Directory", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        self.current_dir_button = customtkinter.CTkButton(
            sidebar_frame, text='../' + self.selected_dir.split('/')[-1], command=self.select_directory)
        self.current_dir_button.grid(row=1, column=0, padx=20, pady=10)

        tkinter.ttk.Separator(sidebar_frame, orient='horizontal').grid(
            row=2, column=0, sticky='we', padx=10, pady=(5, 5))

        # Sidebar --> Heading
        row = 5
        customtkinter.CTkLabel(
            sidebar_frame, text="GUI Menu", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=row, column=0, padx=20, pady=(20, 10))

        # Sidebar --> Buttons
        row += 1
        customtkinter.CTkButton(
            sidebar_frame, text="Overview", command=self.gui_overview).grid(row=row, column=0, padx=20, pady=10)

        row += 1
        customtkinter.CTkButton(
            sidebar_frame, text="Preprocess", command=self.preprocess_tab).grid(row=row, column=0, padx=20, pady=10)

        row += 1
        customtkinter.CTkButton(
            sidebar_frame, text="Setup", command=self.setup_tab).grid(row=row, column=0, padx=20, pady=10)

        row += 1
        customtkinter.CTkButton(
            sidebar_frame, text="Input Text", command=self.input_tab).grid(row=row, column=0, padx=20, pady=10)

        row += 1
        customtkinter.CTkButton(
            sidebar_frame, text="Generate", command=self.generate_tab).grid(row=row, column=0, padx=20, pady=10)

        row += 1
        customtkinter.CTkButton(
            sidebar_frame, text="OCR Check", command=self.ocr_tab).grid(row=row, column=0, padx=20, pady=10)

        row += 1
        tkinter.ttk.Separator(sidebar_frame, orient='horizontal').grid(
            row=row, column=0, sticky='we', padx=10, pady=(5, 5))

        row += 1
        customtkinter.CTkLabel(
            sidebar_frame, text="CSV Menu", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=row, column=0, padx=20, pady=(20, 10))

        row += 1
        customtkinter.CTkButton(
            sidebar_frame, text="Pipeline", command=self.pipeline_overview).grid(row=row, column=0, padx=20, pady=10)

        # row += 1
        # customtkinter.CTkButton(
        #     sidebar_frame, text="CSV Pipeline", command=self.pipeline_tab).grid(row=row, column=0, padx=20, pady=10)

        row += 1
        tkinter.ttk.Separator(sidebar_frame, orient='horizontal').grid(
            row=row, column=0, sticky='we', padx=10, pady=(5, 5))

        # chat
        row += 1
        customtkinter.CTkLabel(
            sidebar_frame, text="AI Chatbot", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=row, column=0, padx=20, pady=(20, 10))

        row += 1
        customtkinter.CTkButton(
            sidebar_frame, text="Chatbot", command=self.chat_tab).grid(row=row, column=0, padx=20, pady=10)

        row += 1
        tkinter.ttk.Separator(sidebar_frame, orient='horizontal').grid(
            row=row, column=0, sticky='we', padx=10, pady=(5, 5))

        # UI
        # row += 1
        # customtkinter.CTkLabel(
        #     sidebar_frame, text="UI", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=row, column=0, padx=20, pady=(20, 10))

        row += 1
        customtkinter.CTkOptionMenu(sidebar_frame,
                                    values=[
                                        "System", "Light", "Dark"],
                                    command=self.change_appearance_mode_event).grid(row=row, column=0, padx=20, pady=(10, 0))
        # row += 1
        # customtkinter.CTkOptionMenu(sidebar_frame,
        #                             values=[
        #                                 "80%", "90%", "100%", "110%", "120%"],
        #                             command=self.change_scaling_event).grid(row=row, column=0, padx=20, pady=(10, 20))

        self.gui_overview()

    # Add details
    def gui_overview(self):
        # Home
        self.top_label = customtkinter.CTkLabel(
            self, text="This tool is built to facilitate the process of building a large custom dataset of images with text imposed on them.\n\nScroll through the tabs below to learn about the various functions.", fg_color="transparent", justify="left")
        self.top_label.grid(row=1, column=1, padx=(
            20, 20), pady=(20, 20), sticky="nsew")

        # Home --> Tabs for functions
        tabview = customtkinter.CTkTabview(self, width=300)
        tabview.grid(row=2, column=1, padx=(
            20, 20), pady=(20, 20), sticky="nsew")
        tabview.add("Preprocess →")
        tabview.add("Setup Template →")
        tabview.add("Input Text →")
        tabview.add("Generate Meme →")
        tabview.add("OCR Check")

        # Home --> Configure grid of individual tabs
        tabview.tab("Preprocess →").grid_columnconfigure(0, weight=1)
        tabview.tab("Setup Template →").grid_columnconfigure(0, weight=1)
        tabview.tab("Input Text →").grid_columnconfigure(0, weight=1)
        tabview.tab("Generate Meme →").grid_columnconfigure(0, weight=1)
        tabview.tab("OCR Check").grid_columnconfigure(0, weight=1)

        customtkinter.CTkLabel(
            tabview.tab("Preprocess →"), justify=LEFT, text='Process all the template images specified in a directory to an uniform format.\n\nUse the toggles to choose which preprocess function to apply.\n\nThe processed images will be stored in {}'.format(PREPROCESSED_TEMPLATES_DIR)).grid(row=0, column=0, padx=20, pady=20)

        customtkinter.CTkLabel(
            tabview.tab("Setup Template →"), justify=LEFT, text='Display each template image specified in a directory and use the mouse to draw input boxes for subsequent text input\n\nUse the left mouse click to mark the top left corner followed by the bottom right corner of the desired bounding box.\n\nYou can use the right mouse click to erase the drawn box.\n\n#Note: if you have preprocessed the image, you should use the images stored in \n\n{}'.format(PREPROCESSED_TEMPLATES_DIR)).grid(row=0, column=0, padx=20, pady=20)

        customtkinter.CTkLabel(
            tabview.tab("Input Text →"), justify=LEFT, text='Display each template image specified in a directory and overlay the drawn input boxes on the image.\n\nUse the left mouse click to select the input box to enter text.\n\nThe selected box will turn green and you can view your inputted text by typing on the keyboard.\n\nIt is not necessary to enter text for all input box. You can choose to enter text in none, any or all of them.\n\nClick on the X button to finish entering the text for current template.\n\nYou can choose to enter multiple captions for the same template. Each set of caption associated with a template will be generated as a separate meme.\n\n#Note: if you have preprocessed the image, you should use the images stored in \n\n{}'.format(PREPROCESSED_TEMPLATES_DIR)).grid(row=0, column=0, padx=20, pady=20)

        customtkinter.CTkLabel(
            tabview.tab("Generate Meme →"), justify=LEFT, text='Use each template image specified in a directory, as well as the associated bounding box and input text,\n\ngenerate the meme in either svg or png format using the selected font.\n\n#Note: if you have preprocessed the image, you should use the images stored in \n\n{}'.format(PREPROCESSED_TEMPLATES_DIR)).grid(row=0, column=0, padx=20, pady=20)

        customtkinter.CTkLabel(
            tabview.tab("OCR Check"), justify=LEFT, text="Use OCR library to verify text extraction from generated memes.\n\nThis is only supported for generated png memes.").grid(row=0, column=0, padx=20, pady=20)

    def preprocess_tab(self):
        self.top_label.configure(
            text='# Note: Make sure the directory is selected in the sidebar before proceeding with the setup!\n\nThis function in the pipeline will convert the images to a unified format / shape depending on the options selected below.\n\nSwitch on / off any of the features and click on the button to preprocess.\n\nImages that are successfully preprocessed are logged in \n{}\n\nImages that failed to preprocess are logged in \n{}.'.format(PREPROCESS_SUCCESS_FILE, PREPROCESS_FAIL_FILE))
        preprocess_frame = customtkinter.CTkFrame(
            self, height=5, fg_color="transparent")
        preprocess_frame.grid(row=2, column=1, padx=(
            20, 20), pady=(20, 20), sticky="nsew")
        preprocess_frame.grid_columnconfigure(0, weight=1)

        # create switch button for preprocess options
        switch_buttons = []
        switch_key_index = {
            0: "resize",
            1: "grayscale",
            2: "normalize",
            3: "scale"
        }

        def create_switch(row_pos, text_label):
            switch = customtkinter.CTkSwitch(
                master=preprocess_frame, text=text_label)
            switch.grid(row=row_pos, column=0, padx=10,
                        pady=(0, 20), sticky="ns")
            return switch

        row_num = 3
        for button_label in switch_key_index.values():
            switch_buttons.append(create_switch(
                row_pos=row_num, text_label=button_label))
            row_num += 1

        def preprocess():
            self.dir_check(self.selected_dir)
            # get selected results and create a map of following format
            # {'resize': 1, 'grayscale': 1, 'normalize': 1, 'scale': 1}
            selected_options = {switch_key_index[index]: button.get(
            ) for index, button in enumerate(switch_buttons)}
            error = preprocess_templates.preprocess(self.selected_dir,
                                                    selected_options)
            self.handle_result(
                "Results are stored in {}.\nLogs are stored in {}.".format(PREPROCESSED_TEMPLATES_DIR, LOGS_DIR), error)

        submit = customtkinter.CTkButton(
            preprocess_frame, text="Preprocess", width=200, height=50, command=preprocess)

        row_num += 1
        submit.grid(row=row_num, column=0, padx=20, pady=20)

    def setup_tab(self):
        self.top_label.configure(
            text='# Note: Make sure the directory is selected in the sidebar before proceeding with the setup!\n\nThis function in the pipeline will display the images in the chosen directory.\nThe user is required to mark the top-left corner, followed by the bottom-right corner of each bounding box of desired input text box.\nThese drawn boxes are where the input text will be placed in the next steps.\n - Use the left mouse button to draw points.\n - Use the right mouse button to erase a drawn rectangle.\n - Press the Esc (Escape) key to switch to the next image.\n\n\n\nUse the "Preview Textbox Coordinate" feature to preview coordinates of a rectangle box.\nPress and hold the left mouse click to draw the box.\nThe corresponding coordinates of drawn boxes is displayed in [top_left_x, top_left_y, bottom_right_x, bottom_right_y] format.\nThis step is useful for for the pipeline approach.\n\n\n\nThe output from this step is stored in \n{}\nYou can also choose to manually adjust the CSV file.'.format(TEXT_COORDINATE_FILE))

        setup_frame = customtkinter.CTkFrame(
            self, height=5, fg_color="transparent")
        setup_frame.grid(row=2, column=1, padx=(
            20, 20), pady=(20, 20), sticky="nsew")
        setup_frame.grid_columnconfigure(0, weight=1)

        def setup():
            self.dir_check(self.selected_dir)
            error = setup_templates.setup(self.selected_dir)
            self.handle_result(
                "Results are stored in {}".format(TEXT_COORDINATE_FILE), error)

        customtkinter.CTkButton(
            setup_frame, text="Setup Templates", width=200, height=50, command=setup).grid(row=3, column=0, padx=20, pady=20)

        def preview():
            self.dir_check(self.selected_dir)
            ImageBoxDrawer(self.selected_dir)

        customtkinter.CTkButton(
            setup_frame, text="Preview Textbox Coordinate", width=200, height=50, command=preview).grid(row=4, column=0, padx=20, pady=20)

    def input_tab(self):
        self.top_label.configure(
            text='# Note: Make sure the directory is selected in the sidebar before proceeding with text input!\n\nDisplay each template image specified in a directory and overlay the drawn input boxes on the image.\n\nUse the left mouse click to select the input box to enter text.\n\nThe selected box will turn green and you can view your inputted text by typing on the keyboard.\n\nIt is not necessary to enter text for all input box. You can choose to enter text in none, any or all of them.\n\nClick on the X button to finish entering the text for current template.\n\nYou can choose to enter multiple captions for the same template. Each set of caption associated with a template will be generated as a separate meme.\n\n\n\nThe output from this step is stored in \n{}\nYou can also choose to manually adjust the CSV file.'.format(TEXT_FILE))

        input_frame = customtkinter.CTkFrame(
            self, height=5, fg_color="transparent")
        input_frame.grid(row=2, column=1, padx=(
            20, 20), pady=(20, 20), sticky="nsew")
        input_frame.grid_columnconfigure(0, weight=1)

        def input_text():
            self.dir_check(self.selected_dir)
            subprocess.run(["python", "text_input.py", self.selected_dir])

        customtkinter.CTkButton(
            input_frame, text="Input Text", width=200, height=50, command=input_text).grid(row=3, column=0, padx=20, pady=20)

    def generate_tab(self, generate_option=1, metadata={}):
        '''
        1 = generation from directory
        2 = generation from csv
        '''
        if generate_option == 1:
            self.top_label.configure(
                text='Generate memes using directory\n\n#Note: Make sure the directory is selected in the sidebar before proceeding with meme generation!\n\nThis function in the pipeline will generate an output based on the selection below.\nSimply click on the button after selecting the desired output to get started.\nIf a template is associated with multiple captions, each set of caption will generate a meme.\n\nThe output will be stored in the following folders:\n- svg: {}\n- png: {}\n\n\n\nFor each selected font type, you can click on the "Preview Font" button to preview the font type.'.format(SVG_PLACED_TEXT_DIR, RESULTS_DIR))
        elif generate_option == 2:
            text = 'Generate memes using CSV\n\n'

            for key, value in metadata.items():
                text += "{}: {}\n\n".format(key, value)

            text += '#Note: Make sure the directory is selected in the sidebar before proceeding with meme generation!\n\nThis function in the pipeline will generate an output based on the selection below.\nClick on the button after selecting the desired output to get started.\nIf a template is associated with multiple captions, each set of caption will generate a meme.\n\nThe output will be stored in the following folders:\n- svg: {}\n- png: {}\n\n\n\nFor each selected font type, you can click on the "Preview Font" button to preview the font type.\n\n'.format(
                SVG_PLACED_TEXT_DIR, RESULTS_DIR)

            self.top_label.configure(
                text=text)

        tab_frame = customtkinter.CTkFrame(
            self, fg_color="transparent")
        tab_frame.grid(row=2, column=1, padx=(
            20, 20), pady=(20, 20), sticky="nsew")
        tab_frame.grid_columnconfigure(0, weight=1)

        # radio buttons
        def create_radio_button(row, label, value):
            customtkinter.CTkRadioButton(master=tab_frame,
                                         text=label,
                                         variable=radio_var,
                                         value=value).grid(
                row=row, column=0, pady=10, padx=200, sticky="ew")

        radio_var = tkinter.IntVar(value=1)
        create_radio_button(
            4, 'Overlay text on template (png format)', 1)
        create_radio_button(
            5, 'Place text for each template at coordinate positions (SVG format)', 2)

        # create_radio_button(3, 'Store SVG texts separately', 3)
        # font selection
        font_menu = customtkinter.CTkOptionMenu(master=tab_frame,
                                                dynamic_resizing=False,
                                                values=list(meme_generator.FONTS_DIR_MAPPING.keys()))
        font_menu.grid(row=6, column=0, padx=20, pady=0)

        # font preview
        font_preview = customtkinter.CTkButton(
            tab_frame, text="Preview Font", width=200, height=50, command=lambda: meme_generator.font_preview(font_menu.get()))
        font_preview.grid(row=8, column=0, padx=0, pady=10)

        # meme generation
        def generate():
            option = radio_var.get()
            out_dir = RESULTS_DIR if option == 1 else SVG_PLACED_TEXT_DIR
            self.dir_check(self.selected_dir)
            error = meme_generator.generate(
                self.selected_dir, option, font_menu.get(), metadata["csv"] if "csv" in metadata.keys() else None)
            self.handle_result(
                "Results are stored in the {} dir".format(out_dir), error)

        customtkinter.CTkButton(
            tab_frame, text="Generate Meme", width=200, height=50, command=generate).grid(row=7, column=0, padx=0, pady=20)

    def ocr_tab(self):
        self.top_label.configure(text='Use OCR to test text extraction on generated memes\n\nThis function in the pipeline will use supported OCR python libraries to extract text.\n\nSupported languages include Chinese Simplified, Malay, Tamil and English.\n\n# Note: By default, the selected directory is \n{}\n\nResults of OCR are stored in \n{}'.format(RESULTS_DIR, OCR_DIR))

        ocr_frame = customtkinter.CTkFrame(
            self, height=5, fg_color="transparent")
        ocr_frame.grid(row=2, column=1, padx=(
            20, 20), pady=(20, 20), sticky="nsew")
        ocr_frame.grid_columnconfigure(0, weight=1)

        # ocr selection
        ocr_menu_map = {
            "tesseract-ocr": 1,
            "easy-ocr": 2
        }
        ocr_menu = customtkinter.CTkOptionMenu(master=ocr_frame,
                                               dynamic_resizing=False,
                                               values=list(ocr_menu_map.keys()))
        ocr_menu.grid(row=5, column=0, padx=20, pady=0)

        def ocr():
            self.dir_check(self.out_dir)
            error = ocr_check.extract_text(
                self.out_dir, ocr_menu_map[ocr_menu.get()])
            self.handle_result(
                "Completed OCR extraction\nYour results are stored in {}".format(OCR_DIR), error)

        customtkinter.CTkButton(
            ocr_frame, text="OCR Check", width=200, height=50, command=ocr).grid(row=6, column=0, padx=20, pady=20)

    def pipeline_overview(self):
        self.top_label.configure(
            text='Quick introduction to the meme generator (CSV)! \n\nThis tool is built to enhance the process of building a large custom dataset of images with text imposed on them.\nThis pipeline omits the "set up" step and "input text" step.\nUser can download a CSV template and enter the metadata (textbox coordinates and caption for each textbox) directly.\nThe filled CSV file can then be uploaded for meme generation\nA meme will be generated for each row of metadata.')

        # Home --> Tabs for functions
        tabview = customtkinter.CTkTabview(self, width=300)
        tabview.grid(row=2, column=1, padx=(
            20, 20), pady=(20, 20), sticky="nsew")

        # preprocess tab
        tabview.add("Preprocess →")
        tabview.tab("Preprocess →").grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(
            tabview.tab("Preprocess →"), justify=LEFT, text='This step follows the same preprocessing.\nIt is recommended that all images are processed to be of the same dimensions.\nThis is to make it simpler to determine the coordinate of textbox in the next step.').grid(row=0, column=0, padx=20, pady=20)
        customtkinter.CTkButton(tabview.tab("Preprocess →"), text="Preprocess",
                                command=self.preprocess_tab).grid(row=1, column=0, padx=20, pady=20)

        # preview tab
        tabview.add("Preview Textbox Coordinates →")
        tabview.tab("Preview Textbox Coordinates →").grid_columnconfigure(
            0, weight=1)
        customtkinter.CTkLabel(
            tabview.tab("Preview Textbox Coordinates →"), justify=LEFT, text='It is necessary for user to specify the location of the textbox so that meme generator can impose text at the correct location.\nUser can use the "Preview Textbox Coordinate" feature to determine the desired textbox coordinates.\nThe coordinate can be copied into the CSV template in the same format i.e. [x1,y1,x2,y2]').grid(row=0, column=0, padx=20, pady=20)
        customtkinter.CTkButton(tabview.tab("Preview Textbox Coordinates →"), text="Preview Textbox Coordinate",
                                command=self.setup_tab).grid(row=1, column=0, padx=20, pady=20)

        # download CSV tab
        tabview.add("Download and Fill Template CSV →")
        tabview.tab("Download and Fill Template CSV →").grid_columnconfigure(
            0, weight=1)
        customtkinter.CTkLabel(
            tabview.tab("Download and Fill Template CSV →"), justify=LEFT, text='A template CSV file is downloaded for the user to fill in.\nThe each row of the csv file is in the following format: \n\nfile_name, [coordinates of textbox A], "caption for textbox A",[coordinates of textbox B], "caption for textbox B"...\n\nFor each row, the user can freely decide the number of textbox and corresponding caption.\nFor example, user can provide 1 coordinate and 1 caption for template_1 in one row, and 2 coordinates and 2 captions for template_1 in next row.\n\nAn example is provided below\n\n0,1,2,3,4\nexample file,"[0,0,0,0]",caption for first box,,,\n2.jpg,"[16, 112, 405, 203]",caption for first box,"[18, 330, 398, 433]",caption for second box\n2.jpg,"[16, 112, 405, 203]",,"[18, 330, 398, 433]",caption for second box\n2.jpg,"[16, 112, 405, 203]",caption for first box,"[18, 330, 398, 433]",,\n2.jpg,"[16, 112, 405, 203]",,,caption for second box\n').grid(row=0, column=0, padx=20, pady=20)

        def download_template():
            self.top_label.configure(
                text='# Note: Select the directory containing template images before proceeding!\n\nThe image names will be automatically filled in the CSV template.\n\nFollow the example and fill in the CSV template.')

            self.dir_check(self.selected_dir)

            # create a pandas frame and export the csv template
            # the csv will be in the format of image_name,"[1,2,3,4]","[1,2,3,4]",A,B
            data = []
            data.append(["example file", "[0,0,0,0]", "caption for first box"])
            for file in os.listdir(self.selected_dir):
                if file.startswith('.'):
                    continue
                data.append([file, "[0,0,0,0]", "caption for first box", "[0,0,0,0]",
                            "caption for second box"])

            df = pd.DataFrame(data)
            df.to_csv(MEME_METADATA_FILE, index=False)
            self.handle_result(
                "Results are stored in {}".format(MEME_METADATA_FILE), None)

        customtkinter.CTkButton(tabview.tab("Download and Fill Template CSV →"), text="Download Template",
                                command=download_template).grid(row=1, column=0, padx=20, pady=20)

        # upload and generate meme
        tabview.add("Upload CSV & Generate Meme →")
        tabview.tab("Upload CSV & Generate Meme →").grid_columnconfigure(
            0, weight=1)
        customtkinter.CTkLabel(
            tabview.tab("Upload CSV & Generate Meme →"), justify=LEFT, text='The user can uploaded the completed CSV to generate the meme. The meme generation process follows the same process.').grid(row=0, column=0, padx=20, pady=20)

        def upload_csv():
            global file_path
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV Files", "*.csv")],
                title="Select a CSV file"
            )

            if file_path:
                self.top_label.configure(
                    text='Selected CSV: {}\n\nProceed to select meme generation options'.format(file_path))

                self.generate_tab(generate_option=2, metadata={
                    "csv": file_path
                })

        customtkinter.CTkButton(tabview.tab("Upload CSV & Generate Meme →"), text="Upload Filled CSV\n& Generate Meme",
                                command=upload_csv).grid(row=1, column=0, padx=20, pady=20)

        # OCR check
        tabview.add("OCR Check")
        tabview.tab("OCR Check").grid_columnconfigure(0, weight=1)
        customtkinter.CTkLabel(
            tabview.tab("OCR Check"), justify=LEFT, text="This step follows the same OCR process").grid(row=0, column=0, padx=20, pady=20)
        customtkinter.CTkButton(tabview.tab("OCR Check"), text="OCR",
                                command=self.ocr_tab).grid(row=1, column=0, padx=20, pady=20)

    def chat_tab(self):
        text = 'A large language model powered chat tool to assist in meme generation ideation.\nThe model and weights being used can be found under the /model directory.\nThe github link to the used model can be found here:\n\nhttps://github.com/antimatter15/alpaca.cpp'

        self.top_label.configure(text=text)

        chat_frame = customtkinter.CTkFrame(
            self, height=5, fg_color="transparent")
        chat_frame.grid(row=2, column=1, padx=(
            20, 20), pady=(20, 20), sticky="nsew")
        chat_frame.grid_columnconfigure(0, weight=1)

        def start_chat():
            self.top_label.configure(
                text=text + "\n\nChat log will be stored in {}".format(CHAT_LOG_FILE))
            threading.Thread(target=ChatWindow()).start()

        customtkinter.CTkButton(
            chat_frame, text="Start Chat", width=200, height=50, command=start_chat).grid(row=6, column=0, padx=20, pady=20)

    # Appearance --> Mode
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # Appearance --> Scale
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    # Working directory selection
    def select_directory(self):
        self.selected_dir = filedialog.askdirectory(initialdir=os.getcwd(),
                                                    title="Select a directory",)
        display_text = '../' + self.selected_dir.split('/')[-1]
        self.current_dir_button.configure(text=display_text)

    def dir_check(self, dir):
        if dir == '' or not dir:
            MessageBox(
                message="[ERROR] Please select a directory from the sidebar first!")

            raise Exception()

    def handle_result(self, success_text, error):
        if error is None:
            MessageBox("[INFO] {}".format(success_text))
        else:
            MessageBox("[ERROR] setup: Failed\n{}".format(error))


if __name__ == "__main__":
    App().mainloop()
