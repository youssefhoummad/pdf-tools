import threading
import time
import tkinter as tk
from tkinter import ttk

import widgets
from mvc import View

h1_opts = {"font":("",16,"bold")}
h2_opts = {"font":("",10,"bold")}
h3_opts = {"font":("",9,"bold")}

pack_opts = {'anchor':'nw', 'padx':20, 'fill':'x'}
frame_opts = {"bg":"#FBFCFE", "highlightbackground":"#E4E5EA", "highlightthickness":1}

PRIMARY_COLOR = "#EFF4F8"




class tkView(View):



    def setup(self, controler, model):
        self.controler = controler
        self.model = model
        # title 1
        ttk.Label(self.parent, text='Pick a File...', **h2_opts, background=PRIMARY_COLOR).pack(**pack_opts)
        self.frame_file().pack(**pack_opts, pady=(0,20))

        self.progressbar = ttk.Progressbar(self.parent, orient='horizontal', mode='determinate', maximum=20)

        # title 2
        self.mainera = widgets.VerticalScrolledFrame(self.parent)        
        self.mainera.pack(fill='both', expand=True)
        

        self.frame_split().pack(**pack_opts, pady=3)
        self.frame_merge().pack(**pack_opts, pady=3)
        self.frame_compress().pack(**pack_opts, pady=3)
        self.frame_image().pack(**pack_opts, pady=3)
        self.frame_crop().pack(**pack_opts, pady=3)
    

    def thread(self, target, *args, **kwargs):
        """ use this methode for make progress bar update"""

        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        # starts thread #
        thread.start()


        self.parent.update()
        self.progressbar.place(x=21, y=120, width=(self.parent.winfo_width()-40), height=10)
        self.progressbar.start()

        # checks whether thread is alive #
        while thread.is_alive():
            self.parent.update()
            pass

    
        self.progressbar.stop()
        self.progressbar['value'] = 100

        self.parent.after(3000, self.progressbar.place_forget)

        # retrieves object from queue #
        # work = self.queue.get()
      
        return #work

    def frame_file(self):
        
        self.header_frame = tk.Frame(self.parent, **frame_opts)
        
        ttk.Label(self.header_frame, text="file name: ").grid(row=0, column=0, sticky='w', pady=(10,0))
        ttk.Label(self.header_frame, text="number of pages: ").grid(row=1, column=0, sticky='w')
        ttk.Label(self.header_frame, text="file size: ").grid(row=2, column=0, sticky='w', pady=(0,10))
        
        ttk.Label(self.header_frame, textvariable=self.model.filename).grid(row=0, column=1, sticky='w')
        ttk.Label(self.header_frame, textvariable=self.model.pages).grid(row=1, column=1, sticky='w')
        ttk.Label(self.header_frame, textvariable=self.model.filesize).grid(row=2, column=1, sticky='w')

        # ttk.Label(self.header_frame, textvariable=self.model.message_flash, **h3_opts).grid(row=1, column=2, sticky='w')

        widgets.Seperator(self.header_frame).grid(row=1, column=2, sticky='nse', padx=(0,30))
        ttk.Button(self.header_frame, text='browse', command=self.controler.browse).grid(row=1, column=3, sticky='e', padx=10)

        self.header_frame.columnconfigure(0, weight=1)
        self.header_frame.columnconfigure(1, weight=6)
        self.header_frame.columnconfigure(2, weight=1)

        return self.header_frame
   
    def frame_split(self):
        _f = widgets.Frame(self.mainera)
        ttk.Label(_f, text='Split the file ', **h2_opts).pack(side='left', padx=10)
        ttk.Label(_f, text='from page: ').pack(side='left', padx=10)
        ttk.Spinbox(_f, from_=1, to=200, textvariable=self.model.start, width=8).pack(sid='left', padx=10)
        ttk.Label(_f, text='to page: ').pack(side='left')
        ttk.Spinbox(_f, from_=1, to=200, textvariable=self.model.end, width=8).pack(side='left')

        ttk.Button(_f, text='Split file', command=self.controler.split).pack(side='right', padx=10)
        widgets.Seperator(_f).pack(side='right', padx=(0,30))

        return _f
    
    def frame_merge(self):
        footer = widgets.Frame(self.mainera, height=360)

        header= widgets.CollapseFrame(self.mainera, target_frame=footer)

        ttk.Label(header, text='merge file width ', **h2_opts).pack(side='left', padx=10)
        ttk.Entry(header, textvariable=self.model.filepath2, width=40, state='readonly').pack(sid='left', padx=10)
        ttk.Button(header, text='Browse', command=self.controler.browse2).pack(side='left', padx=10)

        ttk.Button(header, text='merge files', command=self.controler.merge).pack(side='right', padx=10)
        widgets.Seperator(header).pack(side='right', padx=(0,30))
        
        return header
    
    def frame_image(self):
        _f = widgets.Frame(self.mainera)
        ttk.Label(_f, text='Convert pdf to images', **h2_opts).pack(side='left', padx=10)
        ttk.Checkbutton(_f, text='Extract image from the file', variable=self.model.each_page).pack(side='left', padx=10)
  
        ttk.Button(_f, text='Convert file', command=self.controler.to_images).pack(side='right', padx=10)
        widgets.Seperator(_f).pack(side='right', padx=(0,30))
        return _f
    
    def frame_compress(self):
        _f = widgets.Frame(self.mainera)
        ttk.Label(_f, text='Compress the file', **h2_opts).pack(side='left', padx=10)
  
        ttk.Button(_f, text='Compress', command=self.controler.compress).pack(side='right', padx=10)
        widgets.Seperator(_f).pack(side='right', padx=30)
        return _f

    def frame_crop(self): 
        footer = widgets.Frame(self.mainera, height=360)

        header= widgets.CollapseFrame(self.mainera, target_frame=footer)

        ttk.Label(header, text='Crop margins', **h2_opts).pack(side='left')
        ttk.Label(header, text='top: ').pack(side='left')
        ttk.Spinbox(header, from_=0, to=200, textvariable=self.model.top, width=4).pack(sid='left')
        ttk.Label(header, text='bottom: ').pack(side='left')
        ttk.Spinbox(header, from_=0, to=200, textvariable=self.model.bottom, width=4).pack(side='left')
        ttk.Label(header, text='left: ').pack(side='left')
        ttk.Spinbox(header, from_=0, to=200, textvariable=self.model.left, width=4).pack(sid='left')
        ttk.Label(header, text='right: ').pack(side='left')
        ttk.Spinbox(header, from_=0, to=200, textvariable=self.model.right, width=4).pack(side='left')

        ttk.Button(header, text='Crop file', command=self.controler.crop).pack(side='right', padx=10)
        widgets.Seperator(header).pack(side='right', padx=(0,30))

        ttk.Spinbox(footer, from_=0, to=200, textvariable=self.model.right, width=4).pack(side='left', padx=10, pady=20)

        self.footer = footer
        return header


    def flash(self, type_flash='error', message=None):

        # get frame positon and make scroll bar go to his position
        # pos = self.parent.winfo_height() / self.footer.winfo_rooty()
        # print(pos)
        # self.scrollbar.yview_moveto(pos)

        def colorize(color1='#E4E5EA', color2='#FBFCFE'):
            self.header_frame.config(highlightbackground=color1,  background=color2)
            for w in self.header_frame.winfo_children():
                try:
                    w.config(background=color2)  # type: ignore
                except:
                    pass
            self.parent.update_idletasks()
        

        colors_flash = {'color1':'red','color2':'#ffeaf5'}
        
        if type_flash == 'success':
            colors_flash = {'color1':'green','color2':'#d0f0ec'}

        self.model.message_flash.set(message)
            
        colorize(**colors_flash)
        self.parent.after(60, None)            
        colorize()
        self.parent.after(50, None)            
        colorize(**colors_flash)
        self.parent.after(40, None)            
        colorize()
        self.parent.after(30, None)            
        colorize(**colors_flash)
        self.parent.after(3000, colorize)
        self.parent.after(3000, lambda: self.model.message_flash.set(""))

        # self.model.message_flash.set("")

