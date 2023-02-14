from abc import abstractmethod

P_X = 0
P_Y = 1
P_W = 2
P_H = 3
T_X = 4
T_Y = 5
T_W = 6
T_H = 7

ABSOLUTE_MAP = {}
RELATIVE_MAP = {}
COMPOUND_MAP = {}

def ABSOLUTE(toChange, value):
    key = f'{toChange}|{value}'
    if key in ABSOLUTE_MAP: return ABSOLUTE_MAP[key]
    ABSOLUTE_MAP[key] = AbsoluteConstraint(toChange, value)
    return ABSOLUTE_MAP[key]

def RELATIVE(toChange, value, relativeTo):
    key = f'{toChange}|{value}|{relativeTo}'
    if key in RELATIVE_MAP: return RELATIVE_MAP[key]
    RELATIVE_MAP[key] = RelativeConstraint(toChange, value, relativeTo)
    return RELATIVE_MAP[key]

def COMPOUND(first, second):
    key = f'{first}|{second}'
    if key in COMPOUND_MAP: return COMPOUND_MAP[key]
    COMPOUND_MAP[key] = CompoundConstraint(first, second)
    return COMPOUND_MAP[key]

class ConstraintManager:
    def __init__(self, pos, dim):
        self.pos = pos
        self.dim = dim

    def calcConstraints(self, *constraints):
        constraints = [*constraints]
        if len(set(c.toChange for c in constraints)) != 4:
            raise Exception('Incorrect number of constraints') 
        transform = [*self.pos, *self.dim, *([0]*4)]
        isSet = [*([True]*4), *([False]*4)]
        while len(constraints) > 0:
            current = None
            for c in constraints:
                if current != None: raise Exception('Missing dimension in constraints') 
                if not c.validTransform(isSet): continue
                current = c
                break
            if current == None: raise Exception('Constraints can not be solved')
            current.adjustTransform(transform, isSet)
            constraints.remove(current)
        return (transform[4], transform[5], transform[6], transform[7])

class Constraint:
    def __init__(self, toChange):
        self.toChange = toChange

    @abstractmethod
    def adjustTransform(self, transforms, isSet):
        ...
    
    @abstractmethod
    def validTransform(self, isSet):
        ...

class AbsoluteConstraint(Constraint):
    def __init__(self, toChange, value):
        super().__init__(toChange)
        self.value = value
    
    def adjustTransform(self, transforms, isSet):
        transforms[self.toChange] = self.value;
        isSet[self.toChange] = True;
    
    def validTransform(self, isSet):
        return True

class RelativeConstraint(Constraint):
    def __init__(self, toChange, value, relativeTo):
        super().__init__(toChange)
        self.value = value
        self.relativeTo = relativeTo
    
    def adjustTransform(self, transforms, isSet):
        transforms[self.toChange] = transforms[self.relativeTo]*self.value
        isSet[self.toChange] = True
    
    def validTransform(self, isSet):
        return isSet[self.relativeTo]

class CompoundConstraint(Constraint):
    def __init__(self, constraint1, constraint2):
        super().__init__(constraint1.toChange)
        self.constraint1 = constraint1
        self.constraint2 = constraint2
    
    def adjustTransform(self, transforms, isSet):
        prev = transforms[self.toChange];
        self.constraint1.adjustTransform(transforms, isSet);
        change = transforms[self.toChange] - prev;
        transforms[self.toChange] = prev;
        self.constraint2.adjustTransform(transforms, isSet);
        transforms[self.toChange] += change;

    def validTransform(self, isSet):
        return self.constraint1.validTransform(isSet) and self.constraint2.validTransform(isSet);
