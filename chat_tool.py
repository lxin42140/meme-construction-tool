import tkinter as tk
import subprocess
import threading
from config import *
import datetime
import re

USER = "user"
MODEL = "alpaca"


terminal_process = subprocess.Popen(["./scripts/start_chat.sh"],
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)


class ChatWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("AI Chat")

        # Create a common widget to display the terminal output and user input
        self.text_widget = tk.Text(self, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Create a separate input widget
        self.input_widget = tk.Text(self, wrap=tk.WORD, height=1)
        self.input_widget.pack(fill=tk.X)
        self.input_widget.bind("<Return>", self.send_command)
        self.input_widget.focus_set()

        # Start a separate thread to continuously read the terminal output
        self.stdout_thread = threading.Thread(
            target=self.read_output, args=(terminal_process.stdout, 'stdout')).start()
        # self.stderr_thread = threading.Thread(
        #     target=self.read_output, args=(terminal_process.stderr, 'stderr')).start()

        self.update_text_widget("========\nThis is a chat tool support with Alpaca 7B model, and is running locally with no internet connection required. There is no security filter for this model, hence you can use this tool to assist the generation of both hateful memes and okay memes.\n\nTo start, simply type in the input box at the bottom of the screen and press <Enter>. Note that the model may take a few seconds before replying.\n\nTo end, close this window.\n========\n")

        # start window
        self.mainloop()

    def read_output(self, pipe, output_type):
        for line in iter(pipe.readline, b''):
            line = line.decode().strip() + "\n \n"

            # use regex to remove logging info like "[1m"
            line = re.sub(r'\[+\d+m', '', line)

            # show on text widget
            self.update_text_widget(line)

            # log user input
            self.log_text(MODEL, line)

    def update_text_widget(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)
        self.update_idletasks()

    def send_command(self, event):
        # get user input
        user_input = self.input_widget.get("1.0", tk.END).strip()
        # clear input widget
        self.input_widget.delete("1.0", tk.END)

        # flush user input
        user_input += "\n"
        terminal_process.stdin.write(user_input.encode())
        terminal_process.stdin.flush()

        # write user input to output widget
        self.update_text_widget("User: " + user_input)

        # log user input
        self.log_text(USER, user_input)

    def log_text(self, label, text):
        with open(CHAT_LOG_FILE, "a") as f:
            f.write("{} - {}: {}".format(label, datetime.datetime.now().strftime(
                "%d-%m-%y %H:%M:%S"), text))


if __name__ == "__main__":
    ChatWindow()
