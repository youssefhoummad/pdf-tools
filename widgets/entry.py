import tkinter as tk
from tkinter import ttk


# has placeholder
class Entry(ttk.Entry):
    """A custom Entry widget with placeholder text functionality and validation.
    Attributes:
        placeholder (str): The placeholder text to display when the entry is empty.
        command (callable): A function to call when the entry content changes.
    Methods:
        configure(*args, **kwargs):
            Configures the state of the entry widget, enabling or disabling it.
        validate(*_):
            for sv_ttk theme only
            Validates the entry content, marking it as invalid if it is not.
        remove_placeholder(event):
            Removes the placeholder text when the entry gains focus.
        add_placeholder(event):
            Adds the placeholder text back if the entry is empty when it loses focus.
        check_empty(event):
            Checks if the entry is empty and handles the placeholder text accordingly.
        get():
            Returns the current content of the entry, excluding the placeholder text.
    """
    def __init__(self, master=None, placeholder="", validator=None, **kwargs):
        super().__init__(master, **kwargs)

        self.validator = validator or self.default_validator

        self.placeholder = placeholder
        super().insert(0, placeholder)

        # Bind events for removing and adding placeholder
        self.bind("<FocusIn>", self.remove_placeholder)
        self.bind("<FocusOut>", self.add_placeholder)
        self.bind("<KeyRelease>", self.check_empty)

    def default_validator(self, *_):
        return True


    def configure(self, *args, **kwargs):
        if kwargs.get("state") == "enable":
            super().config(state="enable")
            self.add_placeholder(None)

        if kwargs.get("state") == "disable":
            super().delete(0, 'end')
            self.state(["!invalid"])
            super().config(state="disable")


    config = configure


    def validate(self, *_):
        """
        This method invalidates the entry if its content is not an integer
        """
        if self.validator(self.get()):
            self.state(["!invalid"])
        else:
            self.state(["invalid"])


 
    def remove_placeholder(self, event):
        """Remove placeholder text when the user clicks into the entry field."""

        color = self.tk.call("ttk::style", "lookup", "TEntry", "-foreground")
        if super().get() == self.placeholder:
            super().configure(foreground=color)
            self.delete(0, 'end')
        



    def add_placeholder(self, event):
        """Add placeholder text back if the entry is empty."""
        # self.bind("<FocusOut>", self.validate_int)

        if super().get() == "":
            super().configure(foreground='gray')
            self.insert(0, self.placeholder)


    def check_empty(self, event):
        """Check if the entry is empty and handle placeholder."""

        if super().get() == "":
            self.add_placeholder(event)
        
        if super().get() == self.placeholder:
            self.remove_placeholder(event)
        
        self.validate()
        


    def get(self):
        if super().get() == self.placeholder:
            return ""
        return super().get()
        



if __name__ == "__main__":
    def validate_int(astr:str) -> bool:
        return astr.isdigit()
    
    root = tk.Tk()
    root.geometry("200x200")
    entry = Entry(root, placeholder="Enter a number", validator=validate_int)
    entry.pack()
    root.mainloop()