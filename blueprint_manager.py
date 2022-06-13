#created by Antoine Buirey
#the goal of this application is to create a blueprint manager for space engineers
#it will allow you to download and install blueprints from steam and to manage them (update, delete,etc)

from time import sleep
import tkinter as tk
from subprocess import call
import sys
from json import loads, dumps
import shutil
from xml.etree import ElementTree as ET
from os import listdir,mkdir
from exeptions import BlueprintNotFound
from PIL import Image, ImageTk
from webbrowser import open_new_tab

from threading import Thread

def INIT():
    #init the application from the json file paths.json
    global PATH
    global STEAMCMD_PATH
    global BLUEPRINTS
    global DISABLED_PATH

    with open("paths.json", "r") as f:
        paths = loads(f.read())
        PATH = paths["path"]
        STEAMCMD_PATH = paths["steamcmd"]
        BLUEPRINTS = paths["blueprints"]
        DISABLED_PATH = paths["disabled"]


PATH = '\\'.join(sys.argv[0].split('/')[:-1])                                                                       #TODO remove these 4 lines
BLUEPRINTS = "C:/spaceengineers/blueprints"
DISABLED_PATH = PATH+"/disabled"
STEAMCMD_PATH = "C:/steamcmd"

#INIT()                                                                                                             #TODO : create the file paths.json and activate this line

if not "disabled" in listdir(PATH):
    mkdir(DISABLED_PATH)

URL = "https://steamcommunity.com/sharedfiles/filedetails/?id=%d"

def download(mod_id):
    print("Downloading %d from steam" % mod_id, end="")
    exe = "/steamcmd.exe"
    login = ["+login", "anonymous"]
    app_id = 244850
    quit = "+quit"
    logfile = "C:/spaceengineers/logs/"+str(mod_id)+".log"
    log_arg = "> "+logfile
    fh = open("NUL", 'w')
    res = call([STEAMCMD_PATH+exe]+login+["+workshop_download_item %d %d" % (int(app_id), int(mod_id)), quit, log_arg], stdout = fh, stderr = fh)
    fh.close()
    if str(mod_id) in listdir(STEAMCMD_PATH+"/steamapps/workshop/content/%d" % app_id):
        print("\t[OK]")
        return True,STEAMCMD_PATH+"/steamapps/workshop/content/%d/%d" % (int(app_id), int(mod_id))
    else:
        print("\t[FAIL]")
        return False,None

class Storage:
    '''
    Handle the storage of all blueprints in the storage.json file
    '''
    def __init__(self):
        self.filepath = PATH+"/storage.json"
        self.data = {}
        self.load()

    def append(self, blueprint):
        if any(blueprint['id'] == bl['id'] for bl in self.data):
            for i in range(len(self.data)):
                if self.data[i]['id'] == blueprint['id']:
                    self.data[i] = blueprint
                    break
        else:
            self.data.append(blueprint)
        self.save()

    def load(self):
        try:
            with open(self.filepath, "r") as f:
                self.data = loads(f.read())
        except FileNotFoundError:
            self.save()
        except Exception as e:
            print(e)
            
    def save(self):
        with open(self.filepath, "w") as f:
            f.write(dumps(self.data))
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __repr__(self):
        return "<Storage: %s>" % self.data

    def __str__(self):
        return str(self.data)

    def __contains__(self, key):
        #verify if key is in storage in "id" or "name" field
        return len(self.select(id = key)) > 0 or len(self.select(name = key)) > 0

    def select(self, **kwargs : dict)-> list:
        #return a list of all blueprints where key match with value
        res = []                
        for blueprint in self.data:
            if all(blueprint[key] == value for key, value in kwargs.items()):
                res.append(blueprint)
        return res

    def get_ids(self):
        return [blueprint["id"] for blueprint in self.data]

    def delete(self, **kwargs : dict):
        #delete all blueprints where key match with value
        for i in range(len(self.data)):
            blueprint = self.data[i]
            if all(blueprint[key] == value for key, value in kwargs.items()):
                self.data.pop(i)
                break
        self.save()


    

class Blueprint:
    def __init__(self,id):
        self.storage = Storage()
        self.id = int(id)
        if  len(self.storage.select(id = self.id)) >= 1:
            self.active = self.storage.select(id = id)[0]['active']
            self.name = self.storage.select(id = id)[0]['name']
            if not self.name in listdir(BLUEPRINTS) and not self.name in listdir(DISABLED_PATH):
                res = self.download()
                if not res:
                    raise BlueprintNotFound(self)
        else:
            res = self.download() 
            if not res:
                raise BlueprintNotFound(self)
        self.path = BLUEPRINTS+"/"+self.name if self.active else DISABLED_PATH+"/"+self.name

    
    def download(self):
        res = download(self.id)
        if res[0]:
            self.active = True
            self.name = self.get_name(res[1])
            self.save_at(res[1])
            self.storage.append({'id': self.id,'active':self.active,'name':self.name})
            return True
        else:
            return False

    def save_at(self, current_name: str):
        #move the folder in the blueprints folder
        print("Creating the '%s' folder" % self.name, end = "")
        try:
            #try to create the folder
            mkdir(BLUEPRINTS+"/"+self.name)
            print("\t[OK]")
        except FileExistsError as e:
            #the folder already exists, so we don't need to create it
            print("\t[FOLDER ALREADY EXIST]")
        print("Moving all files to the '%s' folder" % self.name, end = "")
        for file in listdir(current_name):
            #move the files in the new folder
            shutil.move(current_name+"/"+file, BLUEPRINTS+"/"+self.name+"/"+file)
        print("\t[OK]")
        #delete the old folder
        print("Deleting the '%s' folder" % current_name, end = "")
        shutil.rmtree(current_name)
        print("\t[OK]")


    def get_name(self, location: str)-> str:
        #get the name from the attribute subtype in the xml file bp.sbc
        tree = ET.parse(location+"/bp.sbc")
        root = tree.getroot()
        name = tree.find('./ShipBlueprints/ShipBlueprint/Id').attrib['Subtype']
        return name

    def _get_img_name(self):
        for file in listdir(self.path):
            if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg'):
                return file

    def img(self)-> Image.Image:
        if self.active:
            return Image.open(self.path+"/"+self._get_img_name())
        
    def switch(self):
        #if the blueprint is in the blueprints folder, move it to the disabled folder, else move it to the blueprints folder
        if self.active:
            shutil.move(BLUEPRINTS+"/"+self.name,DISABLED_PATH+"/"+self.name)
        else:
            shutil.move(DISABLED_PATH+"/"+self.name,BLUEPRINTS+"/"+self.name)
        self.active = not self.active
        self.storage.append({'id': self.id,'active':self.active,'name':self.name})

    def __repr__(self):
        return "<Blueprint: %s>" % self.name

    def __str__(self):
        return str(self.name)

    def show_on_steam(self):
        #open the blueprint in steam
        open_new_tab(URL%self.id)

    def delete(self):
        #delete the blueprint folder
        print("Deleting %s" % self.name, end = "")
        shutil.rmtree(self.path)
        self.storage.delete(id = self.id)
        print("\t[OK]")

def get_blueprints_folders_content():
    #return the content of the blueprints folder
    return listdir(BLUEPRINTS)+listdir(DISABLED_PATH)


def install(id):
    #install a blueprint
    bp = Blueprint(id)
    return bp


class Threading:
    def download(ids : list):
        #download the blueprints in threads and return the result of them in a dict
        threads = []
        res = {}
        for id in ids:
            t = Thread(target = Threading._download, args = (res, id))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        return res

    def _download(r,i):
        r[i] = download(i)

    def install(ids : list):
        """download and install the blueprints in threads and return the result of them in a dict"""
        threads = []
        res = {}
        for id in ids:
            t = Thread(target = Threading._install, args = (res, id))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        return res

    def _install(r,i):
        r[i] = install(i)
        
