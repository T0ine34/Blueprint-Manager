from doctest import master
from msilib.schema import Error
import subprocess
import sys
from json import loads, dumps
import os
from xml.etree import ElementTree as ET

PATH = '\\'.join(sys.argv[0].split('/')[:-1])

def repr(obj):
    print(obj.__repr__())
    return None


class Steam:
    def __init__(self, user, password=None):
        self.path = "C:\steamcmd"
        self.exe = self.path+"\steamcmd.exe"
        self.login = ["+login", user] if user == "anonymous" else ["+login", user, password]
        self.quit = "+quit"

    def download_mod(self, app_id, mod_id):
        print([self.exe, "+workshop_download_item %d %d" % (app_id, mod_id)])
        res = subprocess.run([self.exe]+self.login+ ["+workshop_download_item %d %d" % (app_id, mod_id), self.quit])
        if res.returncode == 0:
            return True,self.path+"\steamapps\workshop\content\%d\%d" % (app_id, mod_id)
        else:
            return False,None

    def __repr__(self):
        return "<Steam: %s>" % self.login

class Storage:
    '''
    Handle the storage of all blueprints in the storage.json file
    '''
    def __init__(self):
        self.filepath = PATH+"\storage.json"
        self.data = {}
        self.load()

    def load(self):
        try:
            with open(self.filepath, "r") as f:
                self.data = loads(f.read())
        except FileNotFoundError:
            self.save()
        except Error as e:
            print(e)
            

    def save(self):
        with open(self.filepath, "w") as f:
            f.write(dumps(self.data))
    
    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

    def __repr__(self):
        return "<Storage: %s>" % self.data


class Mod:
    def __init__(self, name, id, path,master):
        self.name = name
        self.id = id
        self.path = path
        self.master = master
        self.type = 'blueprint'

    def __repr__(self):
        return "<Mod: %s at %s>" % (self.name, self.path)

    def move_on(self, path):
        self.path = path
        self.master.storage[elf.]
    
    @staticmethod
    def SpaceEngineers(location,master):
        id = location.split("\\")[-1]
        tree = ET.parse(location+'\\bp.sbc')
        root = tree.getroot()
        name = tree.find('./ShipBlueprints/ShipBlueprint/Id').attrib['Subtype']
        return Mod(name, id, location,master)


class Main:
    def __init__(self):
        self.storage = Storage()
        self.steam_link = Steam("anonymous")
        self.games = self.storage['games']

    def download_mod(self, app_id, mod_id):
        res = self.steam_link.download_mod(app_id, mod_id)
        if res[0]:
            mod = Mod.SpaceEngineers(res[1],self)

            self.storage['mods'][app_id] = {'id': mod_id, 'type': mod.type,'name'  : mod.name, 'path': 'steam'}
            self.storage.save()
            return True
        else:
            return False
    
m = Main()
m.download_mod(244850, 2813101218)