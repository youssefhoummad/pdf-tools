
import tkinter as tk

from PIL import Image, ImageTk



class Canvas(tk.Canvas):
    def __init__(self, master, model, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.model = model

        self.height = kwargs.get('height', 400)
        self.width = kwargs.get('width', 294)

        self.config(highlightthickness=0, bd=0, bg='white', width=self.width, height=self.height)

        self.model.top.trace('w', self.on_change_line_top)
        self.model.bottom.trace('w', self.on_change_line_bottom)
        self.model.right.trace('w', self.on_change_line_right)
        self.model.left.trace('w', self.on_change_line_left)


        self.line_top = self.create_line(-1, -1, self.width,-1, fill="red")
        self.line_bottom = self.create_line(0, self.height, self.width, self.height, fill="red")
        self.line_left = self.create_line(-1, -1, -1, self.height, fill="red")
        self.line_right = self.create_line(self.width, 0, self.width, self.height, fill="red")


        self._textpreview = self.create_text(self.width//2, self.height//2, text="P R E V I E W", font='bold',fill='gray')
    
    def on_change_line_top(self, *args):
        self.coords(self.line_top, 0, self.model.top.get(), self.width, self.model.top.get())


    def on_change_line_bottom(self, var, indx, mode):
        bottom = self.height - int(self.model.bottom.get())
        self.coords(self.line_bottom, 0, bottom, self.width, bottom)


    def on_change_line_left(self, var, indx, mode):
        left = int(self.model.left.get())
        self.coords(self.line_left, left, 0, left, self.height)


    def on_change_line_right(self, var, indx, mode):
        right = self.width - int(self.model.right.get())
        self.coords(self.line_right, right, 0, right, self.height)
    
    def show_image(self, img):
        org_w = img.width # memorize origine width
        img.thumbnail((self.width , self.height), Image.Resampling.LANCZOS)

        self.model.zoom_thumbnail = org_w / img.width

        self.config(height=img.height)
        self.height = img.height

        self.cover = ImageTk.PhotoImage(img)
        self.thumbnail = self.create_image(img.width/2, img.height/2, image=self.cover)
        self.tag_lower(self.thumbnail)
        self.tag_lower(self._textpreview)
    
    def clean(self):
        self.delete(self.thumbnail)



