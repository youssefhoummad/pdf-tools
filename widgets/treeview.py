from tkinter import ttk
from typing import Callable


# width move up methods
class Treeview(ttk.Treeview):
    def __init__(self, parent, on_select:Callable, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bind("<<TreeviewSelect>>", self.on_row_select)

        self.on_select = on_select
    
    
    def move_up(self, *args, **kwargs):
        leaves = self.selection()
        for i in leaves:
            self.move(i, self.parent(i), self.index(i)-1)


    def move_down(self, *args, **kwargs):
        leaves = self.selection()
        for i in reversed(leaves):
            self.move(i, self.parent(i), self.index(i)+1)
    

    def remove_item(self, *args, **kwargs):
        leaves = self.selection()
        if leaves:
            self.delete(leaves[0])



    def on_row_select(self, *args, **kws):
        selected_item = self.selection()
        if selected_item:
            values = self.item(selected_item[0], 'values')
            self.on_select(values)


if __name__ == '__main__':
    import tkinter as tk   
    root = tk.Tk()
    tree = Treeview(root, lambda x: print(x),  columns=("A", "B", "C"), show='headings')
    tree.pack()
    tree.insert("", "end", values=("1", "2", "3"))
    tree.insert("", "end", values=("4", "5", "6"))
    root.mainloop()