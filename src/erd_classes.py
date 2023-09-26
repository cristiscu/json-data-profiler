"""
Created By:    Cristian Scutaru
Creation Date: Sep 2023
Company:       XtractPro Software
"""

from json_classes import JsonManager, Val, Prop, Obj, Arr

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

# ==========================================================================
class ERDManager:
    def __new__(cls):
        raise TypeError("This is a static class and cannot be instantiated.")

    tables = {}
    obj = None
    show_types = True
    remove_dups = False

    @classmethod
    def getTables(cls, obj):
        cls.tables = {}
        cls.obj = obj
        if isinstance(obj, Arr):
            for o in obj.objs:
                cls._getTable(o, True)
        else:
            cls._getTable(obj, True)
        return cls.tables

    @classmethod    
    def getTopObjName(cls):
        return "JSON ARRAY" if isinstance(cls.obj, Arr) else "JSON OBJECT"

    @classmethod
    def _getTable(cls, obj, isTop=False):
        if obj.name in cls.tables:
            return cls.tables[obj.name]

        table = Table(obj, obj.name)
        cls.tables[obj.name] = table
        table.isTop = isTop
        for key in obj.props:
            prop = obj.props[key]
            col = Column(table, prop, prop.key)
            table.columns.append(col)
            col.nullable = not prop.req
            col.count = prop.count

            if isinstance(prop.val.val, Obj):
                col.datatype = cls._getTable(prop.val.val)
            elif not isinstance(prop.val.val, Arr):
                col.datatype = prop.val.type
            elif prop.val.val.hasPrimitives():
                col.datatype = f"{prop.val.val.getPrimitiveType()}[]"
            else:
                col.datatype = []
                for o in prop.val.val.objs:
                    col.datatype.append(cls._getTable(o))
        return table

    @classmethod
    def createGraph(cls, tables, theme):
        s = ('digraph {\n'
            + '  graph [ rankdir="RL" bgcolor="#ffffff" ]\n'
            + f'  node [ style="filled" shape="{theme.shape}" gradientangle="180" ]\n'
            + '  edge [ arrowhead="none" arrowtail="normal" dir="both" ]\n\n')

        top_name = cls.getTopObjName()
        top_label = top_name.replace(" ", "_")
        s += (f'  {top_label} [ label="{top_name}"\n'
            + f'    fillcolor="{theme.fillcolorC}" color="{theme.color}" penwidth="1" style="dashed"\n'
            + '  ]\n')

        for name in tables:
            s += tables[name].getDotShape(theme)
        s += "\n"
        for name in tables:
            s += tables[name].getDotLinks(theme)
        s += "}\n"
        return s

# ==========================================================================
class Column:
    def __init__(self, table, prop, name):
        self.table = table
        self.prop = prop
        self.name = name
        self.count = 0
        self.nullable = True
        self.datatype = None        # string/Table

    def getName(self):
        name = self.name
        if self.nullable: name = f"{name}*"
        if ERDManager.show_types and isinstance(self.datatype, list): name += "[]"
        #if JsonManager.show_counts: name = f'{name} ({self.count})'
        return name

    def isSimilarWith(self, col) -> bool:
        if col.nullable != self.nullable: return False
        if isinstance(col.datatype, str) and isinstance(self.datatype, str):
            return col.datatype == self.datatype
        if isinstance(col.datatype, Table) and isinstance(self.datatype, Table):
            return col.datatype.name == self.datatype.name
        if isinstance(col.datatype, list) and isinstance(self.datatype, list):
            for type in self.datatype:
                if type not in col.datatype: return False
            for type in col.datatype:
                if type not in self.datatype: return False
        return True

# ==========================================================================
class Table:
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name
        self.isTop = False
        self.columns = []           # list of all columns

    def getColumn(self, name):
        for column in self.columns:
            if column.name == name:
                return column
        return None

    def isSimilarWith(self, table) -> bool:
        if len(self.columns) != len(table.columns): return False
        for col in self.columns:
            other = table.getColumn(col.name)
            if other is None or not col.isSimilarWith(other): return False
        for col in table.columns:
            other = self.getColumn(col.name)
            if other is None or not col.isSimilarWith(other): return False
        return True

    def getDotShape(self, theme):
        s = self.getDotColumns(theme)
        if len(s) == 0:
            return (f'  {self.name} [fillcolor="{theme.fillcolorC}" color="{theme.color}" penwidth="1" shape="point" label=" "]\n')
        return (f'  {self.name} [\n'
            + f'    fillcolor="{theme.fillcolorC}" color="{theme.color}" penwidth="1"\n'
            + f'    label=<<table style="{theme.style}" border="0" cellborder="0" cellspacing="0" cellpadding="1">\n'
            + s
            + f'    </table>>\n  ]\n')

    def getDotColumns(self, theme):
        s = ""
        for column in self.columns:
            if isinstance(column.datatype, str):
                s += f'      <tr><td align="left"><font color="{theme.icolor}">{column.getName()}&nbsp;</font></td>'
                if ERDManager.show_types:
                    s += f'\n        <td align="left"><font color="{theme.icolor}">{column.datatype}</font></td>'
                s += '</tr>\n'
        return s

    def getDotLinks(self, theme):
        s = ""
        if self.isTop:
            top_name = ERDManager.getTopObjName()
            top_label = top_name.replace(" ", "_")
            dashed = "" if top_name == "JSON OBJECT" else ' style="dashed"'
            s += f'  {self.name} -> {top_label} [ penwidth="{theme.penwidth}" color="{theme.pencolor}"{dashed} ]\n'

        for column in self.columns:
            if not isinstance(column.datatype, str):
                dashed = "" if not column.nullable else ' style="dashed"'
                label = f' label="{column.getName()}"'
                if isinstance(column.datatype, Table):
                    s += (f'  {column.datatype.name} -> {self.name}'
                        + f' [ penwidth="{theme.penwidth}" color="{theme.pencolor}"{dashed}{label} ]\n')
                else:
                    for o in column.datatype:
                        s += (f'  {o.name} -> {self.name}'
                            + f' [ penwidth="{theme.penwidth}" color="{theme.pencolor}"{dashed}{label} arrowtail="crow" ]\n')
        return s
