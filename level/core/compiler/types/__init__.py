from copy import copy
from abc import ABC, abstractmethod

import level.core.ast as ast

class Type:
    def __init__(self, main_type, length=1, sub_types=[], meta_data=None, user_name=None):
        self.main_type = main_type
        self.length = length
        self.sub_types = sub_types
        self.meta_data = meta_data
        self.user_name = user_name
        self.override_size = None

    def size(self):
        if self.main_type.size is None:
            if self.sub_types:
                return self.length * sum([t.size() for t in self.sub_types])
            else:
                raise Exception("You shouldn't be here!")
        else:
            return self.main_type.size

    def __str__(self):
        meta_data_repr = [k[0] for k in self.meta_data] if self.meta_data is not None else None
        return f"Type(main_type={self.main_type.__name__}, length={self.length}, sub_types={[str(t) for t in self.sub_types]}, meta_data={meta_data_repr}, user_name={self.user_name})"

    def __eq__(self, other):
        if type(other) is Type:
            return hash(self) == hash(other)
        else:
            return False

    def __hash__(self):
        return hash((hash(self.main_type.__name__), self.length, tuple(hash(t) for t in self.sub_types), hash(self.user_name)))

    def substitute(self, a, T):
        pass

    def __call__(self, obj):
        res = obj.object_manager.reserve_variable(self)
        res.set(obj)
        return res

class TypeVarException(Exception):
    pass

class TypeVar:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __repr__(self):
        return f"TypeVar({self.name})"

    def __name__(self):
        return "TypeVar"

    @classmethod
    def substitute_ast_element(cls, element, substitute):
        args = []
        key = None

        if type(element) is ast.Type:
            key = element.name

        # we need to add ast.Var because some ast.Call are supposed to be translated int ast.TypeFunctor
        # and then all ast.Var in that ast.Call will be transformed to ast.Type
        # hence the need to replace all template variables in ast.Var
        if type(element) is ast.Var:
            key = element.calling_name

        if key is not None:
            v = TypeVar(key)
            if v in substitute:
                s = substitute[v]

                if type(s) is TypeVar:
                    return ast.Type(substitute[v].name)

                # when types are resolved they might be put in ast element as Type object
                if type(s) is Type:
                    return ast.Type(substitute[v])
            else:
                return element

        for i in range(len(element.args)):
            e = TypeVar.substitute_ast_element(element.args[i], substitute)
            args.append(e)

        element.args = args

        return element

class Obj:
    @abstractmethod
    def set(self, obj):
        pass

    @abstractmethod
    def to_acc(self):
        pass

    @abstractmethod
    def set_by_acc(self):
        pass
