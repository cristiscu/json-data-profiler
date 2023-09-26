"""
Created By:    Cristian Scutaru
Creation Date: Sep 2023
Company:       XtractPro Software
"""

from config import Config
from json_classes import Obj, Arr

# ==========================================================================
class ERDManager:
    tables = {}
    obj = None

    def __new__(cls):
        raise TypeError("This is a static class and cannot be instantiated.")

    @classmethod
    def getEntities(cls, obj):
        cls.tables = {}
        cls.obj = obj
        if isinstance(obj, Arr):
            for o in obj.objs:
                cls._getTable(o, True)
        else:
            cls._getTable(obj, True)
        if Config.remove_dups:
            cls._removeDuplTables()
        return cls.tables

    @classmethod    
    def getTopObjLabel(cls):
        return "JSON_ARRAY" if isinstance(cls.obj, Arr) else "JSON_OBJECT"

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
                col.obj = cls._getTable(prop.val.val)
            elif not isinstance(prop.val.val, Arr):
                col.datatype = prop.val.type
            elif prop.val.val.hasPrimitives():
                col.datatype = f"{prop.val.val.getPrimitiveType()}[]"
            else:
                for obj1 in prop.val.val.objs:
                    col.arr.append(cls._getTable(obj1))
        return table

    @classmethod
    def getEmptyDotShape(cls, label, theme):
        return (f'  {label} [fillcolor="{theme.fillcolorC}" color="{theme.color}"'
            + ' penwidth="1" shape="point" label=" "]\n')

    @classmethod
    def createGraph(cls, theme):
        s = ('digraph {\n'
            + '  graph [ rankdir="RL" bgcolor="#ffffff" ]\n'
            + f'  node [ style="filled" shape="{theme.shape}" gradientangle="180" ]\n'
            + '  edge [ arrowhead="none" arrowtail="normal" dir="both" ]\n\n'
            + cls.getEmptyDotShape(cls.getTopObjLabel(), theme))

        for name in cls.tables: s += cls.tables[name].getDotShape(theme)
        s += "\n"
        for name in cls.tables: s += cls.tables[name].getDotLinks(theme)
        s += "}\n"
        return s
    
    @classmethod
    def _removeDuplTables(cls):
        while True:
            table1, table2 = cls._findSimilar()
            if table1 is None: return
            cls._replaceTable(table1, table2)

    @classmethod
    def _findSimilar(cls):
        for key1 in cls.tables:
            table1 = cls.tables[key1]
            for key2 in cls.tables:
                table2 = cls.tables[key2]
                if table1 != table2 and table1.isSimilarWith(table2):
                    return table1, table2
        return None, None

    @classmethod
    def _replaceTable(cls, table1, table2):
        for key in cls.tables:
            table = cls.tables[key]
            for col in table.columns:
                if col.obj is not None and col.obj == table1:
                    col.obj = table2
                elif len(col.arr) > 0:
                    for obj in col.arr:
                        if obj == table1:
                            col.arr.remove(table1)
                            col.arr.append(table2)
        del cls.tables[table1.name]

# ==========================================================================
class Column:
    def __init__(self, table, prop, name):
        self.table = table
        self.prop = prop
        self.name = name
        self.count = 0
        self.nullable = True

        self.datatype = None        # string, string[]
        self.obj = None             # Table
        self.arr = []               # [Table, ...] <-- array of array?

    def getName(self):
        name = self.name
        if self.nullable: name = f"{name}*"
        if Config.show_types and len(self.arr) > 0: name += "[]"
        #if JsonManager.show_counts: name = f'{name} ({self.count})'
        return name

    def isSimilarWith(self, col) -> bool:
        if col.nullable != self.nullable: return False
        if col.datatype is not None and self.datatype is not None:
            return col.datatype == self.datatype
        if col.obj is not None and self.obj is not None:
            return col.obj == self.obj
        if len(col.arr) > 0 and len(self.arr) > 0:
            for type in self.arr:
                if type not in col.arr: return False
            for type in col.arr:
                if type not in self.arr: return False
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
            return ERDManager.getEmptyDotShape(self.name, theme)
        return (f'  {self.name} [\n'
            + f'    fillcolor="{theme.fillcolorC}" color="{theme.color}" penwidth="1"\n'
            + f'    label=<<table style="{theme.style}" border="0" cellborder="0" cellspacing="0" cellpadding="1">\n'
            + s
            + f'    </table>>\n  ]\n')

    def getDotColumns(self, theme):
        s = ""
        for col in self.columns:
            if col.datatype is not None:
                if not Config.show_types:
                    s += f'      <tr><td align="left"><font color="{theme.icolor}">{col.getName()}</font></td></tr>\n'
                else:
                    s += (f'      <tr><td align="left"><font color="{theme.icolor}">{col.getName()}</font></td>\n'
                        + f'      <td align="left"><font color="{theme.icolor}">{col.datatype}</font></td></tr>\n')
        return s

    def getTopDotLink(self, theme):
        if not self.isTop: return ""
        top_label = ERDManager.getTopObjLabel()
        array = "" if top_label == "JSON_OBJECT" else ' arrowtail="crow" style="dashed"'
        return f'  {self.name} -> {top_label} [ penwidth="{theme.penwidth}" color="{theme.pencolor}"{array} ]\n'

    def getDotLinks(self, theme):
        s = "" if not self.isTop else self.getTopDotLink(theme)
        for col in self.columns:
            if col.datatype is None:
                dashed = "" if not col.nullable else ' style="dashed"'
                label = f' label=<<i>{col.getName()}</i>>'
                if col.obj is not None:
                    s += (f'  {col.obj.name} -> {self.name}'
                        + f' [ penwidth="{theme.penwidth}" color="{theme.pencolor}"{dashed}{label} ]\n')
                else:
                    for obj in col.arr:
                        s += (f'  {obj.name} -> {self.name}'
                            + f' [ penwidth="{theme.penwidth}" color="{theme.pencolor}"{dashed}{label} arrowtail="crow" ]\n')
        return s
