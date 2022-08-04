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
        return str(self) == str(other)

class TypeVar:
    def __init__(self, name):
        self.name = name

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
