from tkinter import Frame, Label


class CardFrame(Frame):
  def __init__(self, parent, title, content, background=None, justify='left'):
    super().__init__(parent, bg='purple')

    if justify=='left':
      anchor = 'nw'
    else:
      anchor = 'se'

    
    self.bg = parent['background']
    self.configure(bg=self.bg)

    Label(self, bg=parent['bg'], text=title, justify=justify,  anchor=anchor,font=('Calibre',22,"bold")).pack(fill="both", pady=(24,0), expand=True)
    Label(self, bg=parent['bg'], text=content,  fg='gray', anchor=anchor,justify=justify, font=('Segoe UI',9,'normal')).pack(fill='both', expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    f = CardFrame(root, "PDF tools", "PDF tools is a collections of tools \nthat will works with pdf fils")
    f.pack(fill='both', expand='True')
    root.mainloop()
