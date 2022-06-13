import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from blueprint_manager import Blueprint, Storage, Threading
import textwrap
from re import split

def list(object = None):
    '''call the mothod __list__ of the object if is defined, else create an empty list'''
    if object is not None and hasattr(object, "__list__"):
        return object.__list__()
    else:
        return []

def resize(img, new_width):
    '''
    Resize an image with the sames proportions
    '''
    width, height = img.size
    ratio = new_width / width
    new_height = int(height * ratio)
    return img.resize((new_width, new_height))

def is_allowed(string):
    #allow a string if it's a number or a numbers separated by a space or a comma
    return string.isdigit() or " ".join(string.split()).replace(",", " ").replace(" ", "").isdigit() or string  == ""

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Space Engineers Blueprint Manager")

        self.max_nb_elt_per_row = 4 # Max number of elements per row

        self.geometry("%dx800"%(self.max_nb_elt_per_row*210))
        
        self.storage = Storage()
        self.blueprints = GUI.Blueprints_List(self)
        self.blueprints.pack_frame(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.input = GUI.Input(self)
        self.input.pack(side=tk.BOTTOM, fill=tk.X)

        self.downloading = GUI.Downloading(self)
        self.downloading.pack(side=tk.BOTTOM, fill=tk.X)

        self.mainloop()
            

    class Blueprints_List(tk.Frame):
        def __init__(self, master):
            '''
            Create the blueprints scrollable list
            '''
            self.parent_frame = tk.Frame(master)
            self.parent_canvas = tk.Canvas(self.parent_frame)
            self.scrollbar = ttk.Scrollbar(self.parent_frame, orient=tk.VERTICAL, command=self.parent_canvas.yview)
            super().__init__(self.parent_canvas)
            self.bind("<Configure>", lambda e: self.parent_canvas.configure(scrollregion=self.parent_canvas.bbox("all")))

            self.master = master

            self.nb_elt_per_row = self.master.max_nb_elt_per_row

            self.blueprints = []

            self.parent_canvas.create_window((0, 0), window=self, anchor="nw")
            self.parent_canvas.configure(yscrollcommand=self.scrollbar.set)

            self.create_widgets()

            self.parent_frame.pack(fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def pack_frame(self,**kwargs):
            self.parent_canvas.pack(**kwargs)
            
        def create_widgets(self):
            column = 0
            row = 0
            for blueprint_id in self.master.storage.get_ids():
                blueprint = Blueprint(blueprint_id)
                tk_blueprint = GUI.Blueprints_List.Tk_Blueprint(self, blueprint)
                self.blueprints.append(tk_blueprint)
                tk_blueprint.grid(column=column, row=row)
                column += 1
                if column >= self.nb_elt_per_row:
                    column = 0
                    row += 1


        def add_blueprint(self, blueprint : Blueprint):
            tk_blueprint = GUI.Blueprints_List.Tk_Blueprint(self, blueprint)
            self.blueprints.append(tk_blueprint)
            tk_blueprint.grid()
            self.update_grid()

        def remove_blueprint(self, blueprint : Blueprint):
            for tk_blueprint in self.blueprints:
                if tk_blueprint.blueprint == blueprint:
                    tk_blueprint.grid_forget()
                    tk_blueprint.destroy()
                    self.blueprints.remove(tk_blueprint)
                    self.update_grid()
                    break
        
        def update(self):
            for tk_blueprint in self.blueprints:
                tk_blueprint.update()

        def update_grid(self):
            column = 0
            row = 0
            for tk_blueprint in self.blueprints:
                tk_blueprint.grid_forget()
                tk_blueprint.grid(column=column, row=row)
                column += 1
                if column >= self.nb_elt_per_row:
                    column = 0
                    row += 1

        #self.blueprint = GUI.Tk_Blueprint(self, Blueprint(2812348784)) #TODO : loop through all blueprints
        #self.blueprint.pack(fill=tk.BOTH, expand=True)



        class Tk_Blueprint(tk.Frame):
            """
            Show a image of the blueprint with his name and a 2 buttons:
            """
            def __init__(self, master, blueprint):
                super().__init__(master)
                self.blueprint = blueprint
                self.master = master
                self.create_widgets()

            def create_widgets(self):
                self.img = self.blueprint.img()
                self.img = resize(self.img, 200)
                self.img = ImageTk.PhotoImage(self.img)
                self.image_lb = tk.Label(self, image= self.img, height=200, width=200)
                self.image_lb.pack()
                self.label = tk.Label(self, text=textwrap.fill(self.blueprint.name, width = 20), font=("Helvetica", 10), width = 20, height = 3) 
                self.label.pack()
                self.button_dl = ttk.Button(self, text="Delete", command=self.delete)
                self.button_dl.pack()
                self.button_switch = ttk.Button(self, text="Enable" if not self.blueprint.active else "Disable", command=self.switch)
                self.button_switch.pack()
                self.button_steam = ttk.Button(self, text="View on Steam", command=self.view_on_steam)
                self.button_steam.pack()

            def switch(self):
                self.blueprint.switch()
                self.button_switch.config(text="Enable" if not self.blueprint.active else "Disable")

            def delete(self):
                self.blueprint.delete()
                self.destroy()

            def view_on_steam(self):
                self.blueprint.show_on_steam()

    class Input(tk.Frame):
        def __init__(self, master):
            super().__init__(master)
            self.master = master
            self.create_widgets()

        def create_widgets(self):
            self.button_dl = ttk.Button(self, text="Add a Blueprint", command=self.add)
            self.button_dl.pack()

        def add(self):
            GUI.Input.Window(self)

        class Window(tk.Toplevel):
            def __init__(self, master):
                super().__init__(master)
                self.master = master
                self.create_widgets()

            def create_widgets(self):
                self.entry = GUI.Input.Window.Entry(self)
                self.entry.pack()
                self.button_dl = ttk.Button(self, text="Download", command=self.download)
                self.button_dl.pack()


            def download(self):
                ids = list(self.entry)
                blueprints = Threading.install(ids)
                for blueprint in blueprints.values():
                    self.master.master.blueprints.add_blueprint(blueprint)
                self.destroy()



            class Entry(tk.Entry):
                def __init__(self, master):
                    self.var = tk.StringVar()
                    super().__init__(master, textvariable=self.var)
                    self.master = master

                    self.old_value = ''

                    self.var.trace('w', self.check)
                    self.get, self.set = self.var.get, self.var.set

                def __iter__(self):
                    self._counter = 0
                    return self
                
                def __next__(self):
                    if self._counter >= len(self.get()):
                        raise StopIteration
                    self._counter += 1
                    return self.get().split(',')[self._counter - 1]

                def __list__(self):
                    return self.get().split(',')


                def check(self, *args):
                    #allow only numbers, empty string and numbers with a comma
                    if is_allowed(self.get()):
                        self.old_value = self.get()
                    else:
                        self.set(self.old_value)
    
    class Downloading(tk.Frame):
        '''
        Show the blueprints that are currently downloading and a progress bar
        '''
        def __init__(self, master):
            super().__init__(master)
            self.master = master

            self.items = []

            self.create_widgets()

        def create_widgets(self):
            self.label = tk.Label(self, text="Downloading blueprints:")
            self.label.pack()

        def add(self, id : int or str):
            blueprint = GUI.Downloading.Item(self, id)
            blueprint.pack()
            self.items.append(blueprint)
            return blueprint
    

g = GUI()