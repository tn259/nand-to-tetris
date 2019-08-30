from enum import Enum


class Kind(Enum):
  STATIC = 0
  FIELD = 1
  ARG = 2
  VAR = 3
  NONE = 4

class VarProperties:
  def __init__(self, varType, kind, index):
    self.varType = varType
    self.kind = kind
    self.index = index

class SymbolTable:
  def __init__(self):
    self.map = {}

  def define(self, name, varType, kind):
    self.map[name] = VarProperties(varType, kind, self.varCount(kind))

  def find(self, name):
    return name in self.map

  def varCount(self, kind):
    count = 0
    for v in self.map.values():
      if v.kind == kind:
        count += 1
    return count

  def kindOf(self, name):
    return self.map[name].kind

  def typeOf(self, name):
    return self.map[name].varType

  def indexOf(self, name):
    return self.map[name].index
