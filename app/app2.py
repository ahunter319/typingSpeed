from tkinter import *
from tkinter import messagebox
from tkstylesheet import TkThemeLoader
import time
import random
import sys
import os
import common


# FUNCTIONS ============================================================================================================

def get_paragraph():
    """
    Generates a random paragraph from list of most common English words.
    :return: paragraph as a list of strings
    """

    paragraph = []
    for x in range(180):
        paragraph.append(random.choice(common.words))

    return paragraph


def resource_path(relative_path):
    """ Get the absolute path to the resource.
    (borrowed from Stackoverflow: https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile) """
    try:
        # Pyinstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# UI ===================================================================================================================
class App(Tk):

    def __init__(self):
        super().__init__()

        # Configure Window
        self.resizable(False, False)
        self.title("Typing Speed")
        icon = resource_path("favicon.ico")
        self.iconbitmap(icon)

        # Attributes
        self.duration = 60000
        self.start_time = 0
        self.total_correct_typed = 0
        self.percent_accuracy = 0
        self.to_update = None

        # Fonts
        self.std_font = ("Lucinda Console", 14)
        self.sml_font = ("Lucinda Console", 12)
        self.crs_font = ("Lucinda Console", 18, "bold")

        # Getting prompt
        self.words = get_paragraph()
        self.sample_text = " ".join(self.words)
        self.n_max = len(self.words) - 1
        self.n = 0

        # UI setup
        self.title("Typing Speed")
        self.config(padx=30, pady=20)

        # Top Label
        Label(self, text="Typing Speed Test", font=self.crs_font).grid(column=1, row=0, columnspan=2)

        # Explanation Label
        Label(self, text="Type the highlighted word and hit 'space' to check. Incorrectly typed words don't count!",
              font=self.sml_font).grid(column=1, row=1, columnspan=2, pady=10)

        # Setting up timer
        self.timer_text = StringVar()
        self.timer = Label(self, textvariable=self.timer_text, font=self.crs_font)
        self.timer.grid(column=2, row=4)
        self.timer_text.set(f"Timer: 0")

        # Text Widget to display prompt
        self.text_paragraph = Text(self, height=13, wrap=WORD, font=self.std_font, spacing2=6, padx=10, pady=10)
        self.text_paragraph.grid(column=1, row=2, columnspan=2)
        self.text_paragraph.insert("1.0", self.sample_text)

        # Getting length of first word in order to properly highlight it
        wrd_ln = len(self.words[0].strip())
        self.text_paragraph.tag_add("start", "1.0", f"1.{wrd_ln}")
        self.text_paragraph.tag_config("start", foreground="red")
        self.text_paragraph["state"] = "disabled"

        # Entry-widget for user to type
        self.typed_text = StringVar()
        self.typed_entry = Entry(self, width=20, font=self.std_font, textvariable=self.typed_text)
        self.typed_entry.grid(column=1, row=3, pady=10)
        self.typed_entry.focus()

        # Reset Button, calls reset method
        Button(self, text="Reset", command=self.reset).grid(column=1, row=4)

        # Loading stylesheet
        theme = TkThemeLoader(self)
        theme_file = resource_path("theme.tkss")
        theme.loadStyleSheet(theme_file)

        # Binding any key to start timer
        self.bind("<Any-KeyPress>", self.start_timer)

    def start_timer(self, event):
        """
        Begins timer by setting start_time to current time. Unbinds all keys and binds only space key to call check_word
        method. Lastly calls update_timer method.
        """

        self.start_time = time.time()
        self.unbind("<Any-KeyPress>")
        self.bind("<space>", self.check_word)
        self.update_timer()

    def update_timer(self):
        """
        Updates timer if passed time has not yet surpassed allowed duration. Displays final score if it has.
        """

        # Converting passed time to milliseconds
        passed_time = round(time.time() - self.start_time)
        milli_time = passed_time * 1000

        # Checking against duration
        if milli_time <= self.duration:

            # Setting timer to current passed time
            self.timer_text.set(f"Timer: {passed_time}")

            # after a second, call update_timer method again
            self.to_update = self.after(1000, self.update_timer)

        else:
            self.unbind("<space>")
            messagebox.showinfo(title="Times up!", message=f"Word Per Minute: {self.total_correct_typed}\nAccuracy: "
                                                           f"{self.percent_accuracy}%")

    def check_word(self, event):
        """
        Checks user-typed word with the current word in paragraph being checked
        """

        # strip trailing space off entry and clear entry widget
        to_check = self.typed_text.get().strip()
        self.typed_text.set("")

        # Checking if typed word matches prompt word
        correct = 0
        if len(to_check) == len(self.words[self.n]):

            for x in range(len(self.words[self.n])):
                if to_check[x] == self.words[self.n][x]:
                    correct += 1

            if correct == len(self.words[self.n]):
                self.total_correct_typed += 1

        # Incrementing prompt-cursor
        self.n += 1

        # Calculating percent accuracy of typed words
        self.percent_accuracy = round((self.total_correct_typed / self.n) * 100, 2)

        # If there are still words left to type, move cursor
        if self.n <= self.n_max:
            self.move_cursor(self.n)
        else:
            self.unbind("<space>")
            self.after_cancel(self.to_update)
            messagebox.showinfo("Out of Words!", message=f"You're out of words. Good work.\n\nWord Per Minute: "
                                                     f"{self.total_correct_typed}\nAccuracy: {self.percent_accuracy}%")

    def move_cursor(self, num):
        """
        Formats and displays paragraph for text widget with current position of word to type in red font.
        """

        # Getting word in prompt at passed cursor location
        current_word = self.words[num].strip()

        # Combining everything before current-word into one string
        start = " ".join(self.words[:num])

        # Combining everything after current-word into one string
        end = " ".join(self.words[num + 1:len(self.words)])

        y = len(current_word)
        z = len(start)

        # Enabling changes to widget
        self.text_paragraph["state"] = "normal"

        # Removing old paragraph
        # NOTE: "1.0" refers to line 1, column 0. As paragraph is all one string, every word is on 'line 1'
        self.text_paragraph.delete("1.0", END)

        # Inserting sections of prompt at appropriate positions
        self.text_paragraph.insert("1.0", start)
        self.text_paragraph.insert(f"1.{z}", f" {current_word} ")
        self.text_paragraph.insert(END, end)

        # Adding tag to location of current-word and changing font to red
        self.text_paragraph.tag_add("cursor", f"1.{z}", f"1.{z + y + 1}")
        self.text_paragraph.tag_config("cursor", foreground="red")

        # Disabling changes to widget
        self.text_paragraph["state"] = "disabled"

    def reset(self):
        """
        Reset entire test to beginning state.
        """

        # Rebinding keys
        self.unbind("<space>")
        self.bind("<Any-KeyPress>", self.start_timer)

        # Resetting counters
        self.n = 0
        self.total_correct_typed = 0
        self.timer_text.set(f"Timer: 0")

        # Only reset to_update if 'after' has been called
        if self.to_update:
            self.after_cancel(self.to_update)

        # Resetting entry
        self.typed_text.set("")

        # Getting new prompt
        self.words = get_paragraph()
        self.sample_text = " ".join(self.words)

        # Enabling edits to text-widget
        self.text_paragraph["state"] = "normal"

        # Inserting new prompt
        self.text_paragraph.delete("1.0", END)
        self.text_paragraph.insert("1.0", self.sample_text)

        # Resetting red-font cursor
        wrd_ln = len(self.words[0].strip())
        self.text_paragraph.tag_add("start", "1.0", f"1.{wrd_ln}")
        self.text_paragraph.tag_config("start", foreground="red")

        # Disabling edits to text-widget
        self.text_paragraph["state"] = "disabled"


# START == =============================================================================================================

app = App()
app.mainloop()



