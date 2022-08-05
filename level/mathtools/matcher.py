from copy import deepcopy, copy
from collections import defaultdict

def udir(obj):
    return list(filter(lambda s: not(len(s) > 1 and s[:2] == '__' and s[-2:] == '__'), dir(obj)))

class GeneralMatcherException(Exception):
    pass

class GeneralMatcher:
    leaf_type_names = {'int', 'float', 'str', 'type', 'method', 'builtin_function_or_method'}
    blank_type_names = {'method', 'builtin_function_or_method', 'NoneType'}

    def __init__(self, var_type):
        self.var_type = var_type

    def validate(self, substitution):
        res = {}
        substitute_map = defaultdict(list)
        for var, value in substitution:
            substitute_map[var].append(value)

        for var in substitute_map:
            values = substitute_map[var]
            for i, v in enumerate(values):
                res[var] = v
                if i > 0 and self.match(values[0], v) is None:
                    return None

        return res


    def match(self, a, b):
        substitution = []
        res = self._match(a, b, substitution)
        if not res:
            return None

        if not substitution:
            return []

        m = self.validate(substitution)
        if m is None:
            return None

        return m

    def _match(self, a, b, substitution):
        # print(a, b)
        if type(a) is self.var_type:
            substitution.append((a, b))
            return True

        if not(type(a) is type(b)):
            return False

        if type(a).__name__ in GeneralMatcher.blank_type_names:
            return True

        if type(a).__name__ in GeneralMatcher.leaf_type_names:
            return a == b

        if type(a) is list or type(a) is tuple:
            if len(a) != len(b):
                return False
            return all([self._match(e, b[i], substitution) for i, e in enumerate(a)])

        if type(a).__module__ == 'builtins':
            # print(type(a))
            # print(type(b))
            raise GeneralMatcherException('type not supported by General Matcher')

        a_attributes = udir(a)
        b_attributes = udir(b)

        a_attributes_set = set(a_attributes)
        b_attributes_set = set(b_attributes)

        if a_attributes_set != b_attributes_set:
            return False

        # print(a_attributes)

        return all([self._match(getattr(a, attr_str), getattr(b, attr_str), substitution) for attr_str in a_attributes])
