from collections import defaultdict

class Inheritance:
    def __init__(self):
        self.parents = defaultdict(set)
        self.ancestors = defaultdict(set)

    def add_inheritance(self, a, b):
        self.parents[a].add(b)
        self.ancestors[a].add(b)

    def is_1st_derived_from_2nd(self, a, b):
        if a not in self.ancestors:
            return False
        if b in self.ancestors[a]:
            return True
        for p in self.parents[a]:
            if self.is_1st_derived_from_2nd(p, b):
                self.ancestors[a].add(b)
                return True
        return False


