from copy import copy
from collections import defaultdict
from abc import ABC, abstractmethod

import level.core.ast as ast

class Type:
    def __init__(self, main_type, length=1, sub_types=[], sub_names=[], meta_data=None, user_name=None):
        self.main_type = main_type
        self.length = length
        self.sub_types = sub_types
        self.sub_names = sub_names
        self.meta_data = meta_data
        self.user_name = user_name
        self.override_size = None
        self._hash = None

    def size(self):
        if self.main_type.size is None:
            if self.sub_types:
                return self.length * sum([t.size() for t in self.sub_types])
            else:
                raise Exception("You shouldn't be here!")
        else:
            return self.main_type.size

    def list_repr(self, types):
        return "[" + ", ".join(map(repr, types)) + "]"

    def __repr__(self):
        return f"Type(main_type={self.main_type.__name__}, length={self.length}, sub_types={self.list_repr(self.sub_types)}, sub_names={self.list_repr(self.sub_names)}, user_name={self.user_name})"

    def __eq__(self, other):
        if type(other) is Type:
            return hash(self) == hash(other)
        else:
            return False

    def reset_hash(self):
        self._hash = None

    def __hash__(self):
        if self._hash is None:
            self._hash = hash((hash(self.main_type.__name__), self.length, tuple(hash(t) for t in self.sub_types), tuple(hash(name) for name in self.sub_names), hash(self.user_name)))
        return self._hash

    def __call__(self, obj):
        res = obj.object_manager.reserve_variable(self)
        res.set(obj)
        return res

    def __add__(self, other):
        if type(other) is not Type:
            return self

        if self.main_type.__name__ != 'Rec':
            return self

        if other.main_type.__name__ != 'Rec':
            return self

        types = {}
        for i, name in enumerate(other.sub_names):
            types[name] = other.sub_types[i], other.meta_data[i]

        for i, name in enumerate(self.sub_names):
            types[name] = self.sub_types[i], self.meta_data[i]

        sub_types = []
        meta_data = []
        sub_names = []
        for name in types:
            T, data = types[name]
            sub_types.append(T)
            meta_data.append(data)
            sub_names.append(name)

        return Type(main_type=self.main_type, length=1, sub_types=sub_types, sub_names=sub_names, meta_data=meta_data)


    @classmethod
    def _match(cls, a, b, substitution):
        if type(a) == list and type(b) == list:
            if len(a) != len(b):
                return False

            return all([Type._match(e, b[i], substitution) for i, e in enumerate(a)])

        if type(a) is TypeVar:
            substitution.append((a, b))
            return True

        if not (type(a) is type(b)):
            return False

        if a.main_type != b.main_type or a.user_name != b.user_name or a.length != b.length or a.sub_names != b.sub_names:
            return False

        if len(a.sub_types) != len(b.sub_types):
            return False

        return all([Type._match(T, b.sub_types[i], substitution) for i, T in enumerate(a.sub_types)])

    @classmethod
    def validate(cls, substitution):
        res = {}
        substitute_map = defaultdict(list)
        for var, value in substitution:
            substitute_map[var].append(value)

        for var in substitute_map:
            values = substitute_map[var]
            for i, v in enumerate(values):
                res[var] = v
                if i > 0 and Type.match(values[0], v) is None:
                    return None

        return res

    @classmethod
    def match(cls, a, b):
        substitution = []
        res = Type._match(a, b, substitution)
        if not res:
            return None

        if not substitution:
            return []

        m = Type.validate(substitution)
        if m is None:
            return None

        return m


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
