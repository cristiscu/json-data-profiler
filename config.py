"""
Created By:    Cristian Scutaru
Creation Date: Sep 2023
Company:       XtractPro Software
"""

import configparser

class Config:
    single_object = True
    remove_dups = True
    show_counts = True
    show_samples = True
    show_types = False
    show_json = False
    show_line_numbers = True

    max_values = 3
    str_truncate = 20

    themes = {}
    theme = None

    def __new__(cls):
        raise TypeError("This is a static class and cannot be instantiated.")
    
    @classmethod
    def loadThemes(cls):
        parser = configparser.ConfigParser()
        parser.read("themes.conf")
        cls.themes = {}
        for section in parser.sections():
            cls.themes[section] = Theme(
                parser.get(section, "color"),
                parser.get(section, "fillcolor"),
                parser.get(section, "fillcolorC"),
                parser.get(section, "bgcolor"),
                parser.get(section, "icolor"),
                parser.get(section, "tcolor"),
                parser.get(section, "style"),
                parser.get(section, "shape"),
                parser.get(section, "pencolor"),
                parser.get(section, "penwidth"))
        return cls.themes

class Theme:
    def __init__(self, color, fillcolor, fillcolorC,
            bgcolor, icolor, tcolor, style, shape, pencolor, penwidth):
        self.color = color
        self.fillcolor = fillcolor
        self.fillcolorC = fillcolorC
        self.bgcolor = bgcolor
        self.icolor = icolor
        self.tcolor = tcolor
        self.style = style
        self.shape = shape
        self.pencolor = pencolor
        self.penwidth = penwidth
