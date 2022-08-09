from copy import copy
from abc import ABC, abstractmethod

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
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((hash(self.main_type.__name__), self.length, hash(tuple(hash(t) for t in self.sub_types)), hash(self.user_name)))

    def substitute(self, a, T):
        pass

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

    def substitute(self, T_exp, T_val):
        if T_exp == self:
            return T_val

        if type(T_exp) is Type:
            res = copy(T_exp)
            res.sub_types = []
            for t in T_exp.sub_types:
                res.sub_types.append(self.substitute(t, T_val))
            return res

        if type(T_exp) is TypeVar:
            return T_exp

        raise TypeVarException()

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
