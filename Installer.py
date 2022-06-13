#this is the installer for any of the toine34 apps

import os
import sys
import tkinter as tk
from tkinter import ttk

from requests import get
from tkhtmlview import HTMLLabel
from markdown import markdown

APP = "Blueprint-Manager" #Must be the name of the github repo


URL = "https://github.com/T0ine34/%s" % APP #! Do not change this
RAWURL = "https://raw.githubusercontent.com/T0ine34/%s" % APP #! Do not change this

def md2html(md):
    '''
    Convert markdown to html
    '''
    return markdown(md)

def load_rules():
    '''
    Load the rules from the rules.md file on github using github api
    '''
    rules = get(RAWURL+"/main/rules.md").text
    if rules != "404: Not Found":
        return md2html(rules)
    else:
        return "Rules not found"
    



class Installer(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Blueprint Manager Installer")
        #set size of window
        self.geometry("600x500")
        self.resizable(False, False)

        self.content = tk.Frame(self, background="white", height=400, width=600)
        self.content.pack(fill="both", expand=True)

        self.current_step = 0 #0 = welcome, 1 = accept conditions, 2 = choose version,3 = choice of paths, 4 = download & install, 5 = finish

        self.next_button = tk.Button(self, text="Next", command=self.next)
        self.previous_button = tk.Button(self, text="Previous", command=self.previous, state="disabled")

        self.rules = load_rules()

        self.__init_steps__()

        self.update_step()

        
        self.next_button.pack(side="right")

        self.previous_button.pack(side="right")

        

    def previous(self):
        self.current_step -= 1
        self.update_step()
        if self.current_step == 0:
            self.previous_button.config(state="disabled")
        elif self.current_step == 4:
            self.next_button.config(text="Install")
        elif self.current_step < 4:
            self.next_button.config(text="Next")
        self.next_button.config(state="normal")
    


    def next(self):
        self.current_step += 1
        self.update_step()
        if self.current_step == 4:
            self.next_button.config(text="Install")
        elif self.current_step == 5:
            self.next_button.config(text="Finish", command=self.close)

        if self.current_step > 0:
            self.previous_button.config(state="normal")
        else:
            self.previous_button.config(state="disabled")

    def close(self):
        self.destroy()

    def __init_steps__(self):
        self.welcome()
        self.accept_conditions()
        self.choose_version()
        self.choose_paths()
        self.download_install()
        self.finish()

    def update_step(self):
        self.f_welcome.pack_forget()
        self.f_accept_conditions.pack_forget()
        self.f_choose_version.pack_forget()
        self.f_choose_paths.pack_forget()
        self.f_download_install.pack_forget()
        self.f_finish.pack_forget()
        if self.current_step == 0:
            self.f_welcome.pack(fill="both", expand=True)
        elif self.current_step == 1:
            self.next_button.config(state="disabled")
            self.f_accept_conditions.pack(fill="both", expand=True)
        elif self.current_step == 2:
            self.f_choose_version.pack(fill="both", expand=True)
        elif self.current_step == 3:
            self.f_choose_paths.pack(fill="both", expand=True)
        elif self.current_step == 4:
            self.f_download_install.pack(fill="both", expand=True)
        elif self.current_step == 5:
            self.f_finish.pack(fill="both", expand=True)

        print(self.current_step)

    #create differents frames for each step. Each frame will be grid in the main window, and start invisible.

    def welcome(self):
        self.f_welcome = tk.Frame(self.content, background="white")
        
        tk.Label(self.f_welcome, text="Welcome to the Blueprint Manager installer", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)
        tk.Label(self.f_welcome, text="This program will guide you through the installation of the Blueprint Manager",
            font="Helvetica 10", background="white").pack(fill="both", expand=True)

        
    def accept_conditions(self):
        self.f_accept_conditions = tk.Frame(self.content, background="white")
        tk.Label(self.f_accept_conditions, text="Accept the following conditions", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True) 
        HTMLLabel(self.f_accept_conditions, html=self.rules, font="Helvetica 10", background="white").pack(fill="both", expand=True)
        self.accept_conditions_var = tk.IntVar()
        self.accept_conditions_var.set(0)
        tk.Checkbutton(self.f_accept_conditions, text="I accept the terms and conditions", variable=self.accept_conditions_var,
            background="white").pack(fill="both", expand=True)
        self.accept_conditions_var.trace("w", self.accept_conditions_changed)


    def accept_conditions_changed(self, *args):
        if self.accept_conditions_var.get() == 1:
            self.next_button.config(state="normal")
        else:
            self.next_button.config(state="disabled")

    def choose_version(self):
        self.f_choose_version = tk.Frame(self.content, background="white")
        tk.Label(self.f_choose_version, text="Choose the version of the Blueprint Manager", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)


    def choose_paths(self):
        self.f_choose_paths = tk.Frame(self.content, background="white")
        tk.Label(self.f_choose_paths, text="Choose the paths of the Blueprint Manager", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)


    def download_install(self):
        self.f_download_install = tk.Frame(self.content, background="white")
        tk.Label(self.f_download_install, text="Download and install the Blueprint Manager", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)

    def finish(self):
        self.f_finish = tk.Frame(self.content, background="white")
        tk.Label(self.f_finish, text="Finish", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)





Installer().mainloop()

