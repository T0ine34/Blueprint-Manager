#this is the installer for any of the toine34 apps

import os
import sys
import tkinter as tk
from tkinter import ttk

from requests import get
from tkhtmlview import HTMLLabel
from markdown import markdown

APP = "Blueprint-Manager" #Must be the name of the github repo


URL = "https://github.com/T0ine34/%s"                           #! Do not change this
RAWURL = "https://raw.githubusercontent.com/T0ine34/%s"         #! Do not change this
APIREPOURL = "https://api.github.com/repos/T0ine34/%s"          #! Do not change this
APIUSERURL = "https://api.github.com/users/T0ine34/repos"       #! Do not change this

def md2html(md):
    '''
    Convert markdown to html
    '''
    return markdown(md)

def load_rules(app):
    '''
    Load the rules from the rules.md file on github using github api
    '''
    rules = get((RAWURL %app )+"/main/rules.md").text
    if rules != "404: Not Found":
        return md2html(rules)
    else:
        return "Rules not found"

def get_releases(app):
    '''
    Load the list of releases from the github api
    '''
    releases = []
    json = get((APIREPOURL %app )+"/releases").json()
    for i in range(len(json)):
        releases.append({'name': json[i]['tag_name'], 'id': json[i]['id']})
    return releases

def get_apps():
    '''
    Load the list of apps from the github api
    '''
    apps = []
    json = get(APIUSERURL).json()
    for i in range(len(json)):
        apps.append({'name': json[i]['name'], 'id': json[i]['id']})
    return apps
    

class Listbox_Scrollable(tk.Frame):
    """
    Listbox with vertical scrollbar
    Usage is the same as the standard Tkinter listbox
    """
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.listbox = tk.Listbox(self, *args, **kwargs)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        __doc__ = self.listbox.__doc__

    def __getattr__(self, attr):
        # Delegate attribute to listbox
        return getattr(self.listbox, attr)

    def bind(self, *args, **kwargs):
        # Delegate bind to listbox
        return self.listbox.bind(*args, **kwargs)

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

        self.list_apps = get_apps()
        self.list_releases = []
        self.rules = ""

        self.__init_steps__()

        self.update_step()

        
        self.next_button.pack(side="right")

        self.previous_button.pack(side="right")

    def get_app_info(self, app):
        """get the info (releases & rules) of the app"""
        self.list_releases = get_releases(app)
        self.rules = load_rules(app)

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
        self.choose_app()
        self.welcome()
        self.accept_conditions()
        self.choose_version()
        self.choose_paths()
        self.download_install()
        self.finish()

    def update_step(self):
        self.f_welcome.pack_forget()
        self.f_choose_app.pack_forget()
        self.f_accept_conditions.pack_forget()
        self.f_choose_version.pack_forget()
        self.f_choose_paths.pack_forget()
        self.f_download_install.pack_forget()
        self.f_finish.pack_forget()
        if self.current_step == 0:
            self.f_welcome.pack(fill="both", expand=True)
        elif self.current_step == 1:
            self.f_choose_app.pack(fill="both", expand=True)
            self.next_button.config(state="disabled")
        elif self.current_step == 2:
            self.next_button.config(state="disabled")
            self.f_accept_conditions.pack(fill="both", expand=True)
        elif self.current_step == 3:
            self.next_button.config(state="disabled")
            self.f_choose_version.pack(fill="both", expand=True)
        elif self.current_step == 4:
            self.f_choose_paths.pack(fill="both", expand=True)
        elif self.current_step == 5:
            self.f_download_install.pack(fill="both", expand=True)
        elif self.current_step == 6:
            self.f_finish.pack(fill="both", expand=True)

    #create differents frames for each step. Each frame will be grid in the main window, and start invisible.


    def welcome(self):
        self.f_welcome = tk.Frame(self.content, background="white")
        
        tk.Label(self.f_welcome, text="Welcome to the Toine34 app installer", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)
        tk.Label(self.f_welcome, text="This program will guide you through the installation of a Toine34 app.",
            font="Helvetica 10", background="white").pack(fill="both", expand=True)


    def choose_app(self):
        """allow the user to choose the app to install and allow him to continue only if he chose an app"""
        self.f_choose_app = tk.Frame(self.content, background="white")
        tk.Label(self.f_choose_app, text="Choose the app you want to install", font="Helvetica 14 bold",
            background="white").pack(fill="both", expand=True)
        self.listbox = Listbox_Scrollable(self.f_choose_app, background="white", height=10, width=30)
        for app in self.list_apps:
            self.listbox.insert("end", app['name'])
        self.listbox.bind("<<ListboxSelect>>", self.choose_app_event)
        self.listbox.pack(fill="both", expand=True)
    
    def choose_app_event(self, event):
        """when the user choose an app, get the info of the app (releases & rules)"""
        self.get_app_info(self.listbox.get(self.listbox.curselection()))
        self.accept_conditions()
        self.choose_version()
        self.next_button.config(state="normal")

        
        
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
        #create a scrollable list of releases
        self.list_releases_var = tk.StringVar()
        if len(self.list_releases) > 0:
            self.list_releases_var.set(self.list_releases[0]['name'])
        
        self.version_menu = Listbox_Scrollable(self.f_choose_version, width = 20, height = 20, listvariable = self.list_releases_var)

        for release in self.list_releases[1:]:
            self.version_menu.insert(tk.END, release['name'])
        self.version_menu.pack()
        self.version_menu.bind("<<ListboxSelect>>", self.choose_version_changed)

    def choose_version_changed(self, *args):
        self.next_button.config(state="normal")




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

