"""
Created By:    Cristian Scutaru
Creation Date: Sep 2023
Company:       XtractPro Software
"""

# ==========================================================================
class JsonManager:
    single_object = False
    show_counts = True
    show_samples = True
    str_truncate = 20
    max_values = 3
    obj_id = 1

    def __new__(cls):
        raise TypeError("This is a static class and cannot be instantiated.")

    @classmethod
    def getTop(cls, data, single_object) -> str:     
        cls.single_object = single_object
        cls.obj_id = 1
        return Obj(data) if isinstance(data, dict) else Arr(data)

    @classmethod
    def getComma(cls, last) -> str: return "" if last else ","
    @classmethod
    def getIndent(cls, level) -> str: return "   " * level

# ==========================================================================
class Val:
    def __init__(self, val, level=0) -> None:
        self.level = level
        self.val = val

        if val is None:
            self.type = "null"; self.val = 'null'
        elif isinstance(val, bool):
            self.type = "bool"; self.val = str(self.val).lower()
        elif isinstance(val, (int, float)):
            self.type = "number"
        elif isinstance(val, list):
            self.type = "array"; self.val = Arr(val, level)
        elif isinstance(val, dict):
            self.type = "object"; self.val = Obj(val, level)
        else:
            self.type = "string"; v = str(self.val).replace('"', '\\"'); self.val = f'"{v}"'

        self.vals = []
        self.addValue(val)

    def isPrimitive(self):
        return self.type not in ["array", "object"]

    def addValue(self, val):
        if self.isPrimitive():
            if val not in self.vals:
                self.vals.append(val)
        elif self.type == "array":
            for x in val:
                if x not in self.vals:
                    self.vals.append(x)

    def _dumpVals(self):
        s = ''; i = 0
        for val in self.vals[0:JsonManager.max_values+1]:
            if i >= JsonManager.max_values: s += ", ..."
            else:
                if isinstance(val, str):
                    val = str(val).replace("\n", " ")
                    if len(str(val)) > JsonManager.str_truncate:
                        val = f'{str(val)[:JsonManager.str_truncate]}...'
                s += f'{", " if len(s) > 0 else ""}{val}'
            i += 1
        return s
    
    def dump(self, last=True, lastVal=False):
        if self.isPrimitive():
            s = "" if last else ", "
            counts = "" if not JsonManager.show_counts else f' ({len(self.vals)})'
            samples = "" if not JsonManager.show_samples else f': {self._dumpVals()}'
            return f'"{self.type}{counts}{samples}"{s}'
        else:
            v = self.val.dump(last, lastVal)
            if lastVal or v.startswith("[ ]") or v.startswith("{ }"):
                return v
            else:
                return f'\n{v}'

# ==========================================================================
class Prop:
    def __init__(self, key, val, level=0) -> None:
        self.level = level
        self.key = key
        self.req = True
        self.count = 1
        self.val = Val(val, level)

    def getName(self):
        req = "" if self.req else "*"
        counts = "" if not JsonManager.show_counts else f' ({self.count})'
        return f'"{self.key}{req}{counts}"'

    def dumpProp(self, last=True, lastVal=False):
        return f'{self.getName()}: {self.val.dump(last, lastVal)}'
    
    def dump(self, last=True, lastVal=False):
        suffix = '' if self.val.type == "object" else '\n'
        if not lastVal:
            lastVal = (self.val.type == "array"
                and (self.val.val.hasPrimitives() or self.val.val.hasSingleProp()))
        return f'{JsonManager.getIndent(self.level)}{self.dumpProp(last, lastVal)}{suffix}'

# ==========================================================================
class Obj:
    def __init__(self, obj, level=0) -> None:
        self.level = level
        self.name = f"n{JsonManager.obj_id}"
        JsonManager.obj_id += 1
        self.props = {}
        for key in obj: self.props[key] = Prop(key, obj[key], level+1)

    def hasSingleProp(self):
        if len(self.props) != 1: return False
        keys = list(self.props.keys())
        return self.props[keys[0]].val.isPrimitive()
    
    def dump(self, last=True, lastVal=False):
        comma = JsonManager.getComma(last)
        keys = list(self.props.keys())
        if len(keys) == 0:
            return f'{{ }}{comma}'
        else:
            prop = self.props[keys[0]]
            if lastVal:
                return f'{{ {prop.dumpProp(last, lastVal)} }}'
            if self.hasSingleProp():
                return f'{JsonManager.getIndent(self.level)}{{ {prop.dumpProp(last, lastVal)} }}\n'

        s = f'{JsonManager.getIndent(self.level)}{{\n'
        for key in self.props: s += self.props[key].dump(key is keys[-1])
        s += f'{JsonManager.getIndent(self.level)}}}{comma}\n'
        return s

# ==========================================================================
class Arr:
    def __init__(self, arr, level=0) -> None:
        self.level = level
        self.objs = []

        for elem in arr:
            if isinstance(elem, list):
                self.objs.append(Arr(elem, level+1))
            elif not isinstance(elem, dict):
                self.objs.append(Val(elem, level+1))
            elif len(self.objs) == 0:
                self.objs.append(Obj(elem, level+1))
            else:
                self._processArrObj(elem, level)

    def _processArrObj(self, elem, level):
        if JsonManager.single_object:
            self._updateObject(elem, level)
        else:
            inst = self._hasSameKeys(elem)
            if inst is None:
                self.objs.append(Obj(elem, level+1))
            else:
                for key in elem:
                    inst.props[key].val.addValue(elem[key])
                    inst.props[key].count += 1

    def _hasSameKeys(self, elem):
        for inst in self.objs:
            if self._hasSameKeysInst(elem, inst):
                return inst
        return None

    def _hasSameKeysInst(self, elem, inst):
        for key in elem:
            if key not in inst.props: return False
        for key in inst.props:
            if key not in elem: return False
        return True

    def _updateObject(self, elem, level):
        inst = self.objs[0]
        for key in inst.props:
            if key not in elem:
                inst.props[key].req = False
            else:
                inst.props[key].val.addValue(elem[key])
                inst.props[key].count += 1
        for key in elem:
            if key not in inst.props:
                inst.props[key] = Prop(key, elem[key], level+2)
                inst.props[key].req = False

    def hasPrimitives(self):
        return (len(self.objs) > 0
            and isinstance(self.objs[0], Val)
            and self.objs[0].isPrimitive())
    
    def getPrimitiveType(self):
        return "array" if not self.hasPrimitives() else self.objs[0].type
    
    def hasSingleProp(self):
        return (len(self.objs) == 1
            and isinstance(self.objs[0], Obj)
            and self.objs[0].hasSingleProp())

    def dump(self, last=True, lastVal=False):
        comma = JsonManager.getComma(last)
        if len(self.objs) == 0:
            return f'[ ]{comma}'
        elif self.hasPrimitives():
            return f'[ {self.objs[0].dump(True, True)} ]{comma}'
        elif self.hasSingleProp():
            return f'[{self.objs[0].dump(True, True)}]{comma}'

        s = f'{JsonManager.getIndent(self.level)}[\n'
        for obj in self.objs:
            d = obj.dump(obj is self.objs[-1])
            s += d if not isinstance(obj, Val) else f'{JsonManager.getIndent(obj.level)}{d}\n'
        s += f'{JsonManager.getIndent(self.level)}]{comma}'
        return s
