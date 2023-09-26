"""
Created By:    Cristian Scutaru
Creation Date: Sep 2023
Company:       XtractPro Software
"""

# ==========================================================================
class Config:
    single_object = True
    remove_dups = True
    show_counts = True
    show_samples = True
    show_types = False
    show_json = False

    max_values = 3
    str_truncate = 20

    def __new__(cls):
        raise TypeError("This is a static class and cannot be instantiated.")

# ==========================================================================
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

    @classmethod
    def getThemes(cls):
        return {
            "Common Gray": Theme("#6c6c6c", "#e0e0e0", "#f5f5f5",
                "#e0e0e0", "#000000", "#000000", "rounded", "Mrecord", "#696969", "1"),
            "Blue Navy": Theme("#1a5282", "#1a5282", "#ffffff",
                "#1a5282", "#000000", "#ffffff", "rounded", "Mrecord", "#0078d7", "2"),
            "Gradient Green": Theme("#716f64", "#008080:#ffffff", "#008080:#ffffff",
                "transparent", "#000000", "#000000", "rounded", "Mrecord", "#696969", "1"),
            "Blue Sky": Theme("#716f64", "#d3dcef:#ffffff", "#d3dcef:#ffffff",
                "transparent", "#000000", "#000000", "rounded", "Mrecord", "#696969", "1"),
            "Common Gray Box": Theme("#6c6c6c", "#e0e0e0", "#f5f5f5",
                "#e0e0e0", "#000000", "#000000", "rounded", "record", "#696969", "1")
        }
