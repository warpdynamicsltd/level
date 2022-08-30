from collections import defaultdict

import level.core.ast as ast
import level.core.parser.code
from level.core.parser.builtin import translate_simple_types


class ImportItem:
    def __init__(self, module_name, alias):
        self.module_name = module_name
        self.alias = alias

    def __repr__(self):
        return repr((self.module_name, self.alias))

class Imports:
    def __init__(self):
        self.module_imports = defaultdict(list)

    def add_import_item(self, source_module, import_item):
        self.module_imports[source_module].append(import_item)

class Normalizer:
    """
    Normalizer takes the whole ast as written by programmer.
    The first it replaces all global, type and subroutine's (but not methods) definition names with module_name:name.
    Next it takes into consideration all imported modules aliases and replace calling_names of elements which are used to
    call globals, subroutines by calling_names where alias is replaced by module name to match definition names.
    """
    def __init__(self, imports, program):
        self.imports = imports.module_imports
        self.program = program
        self.keys = set()
        to_add = list(self.imports.keys())
        for module_name in to_add:
            self.imports[module_name].insert(0, ImportItem(module_name, None))

    def normalize_head_name(self, meta, name):
        source_module = meta.module_name if meta.module_name is not None else 'main'
        return source_module + ':' + name

    def normalize_name(self, meta, name):
        source_module = meta.module_name if meta.module_name is not None else 'main'
        matches = []
        for im in self.imports[source_module]:
            module_name = im.module_name
            alias = im.alias
            if alias is None:
                candidate_name = module_name + ':' + name
                if candidate_name in self.keys:
                    matches.append(candidate_name)
            else:
                if name.startswith(alias):
                    matches.append(module_name + name[len(alias):])

        if not matches:
            return source_module + ':' + name

        if len(matches) > 1:
            raise level.core.parser.code.ParseException(f"can't resolve ambiguous name '{name}' in {meta}")

        return matches[0]

    def normalise(self, element):
        if type(element) is ast.Var and not element.normalized:
            if element.name not in translate_simple_types:
                element.calling_name = self.normalize_name(element.meta, element.name)

        if type(element) is ast.Type and not element.normalized:
            if element.name not in translate_simple_types:
                normalized_name = self.normalize_name(element.meta, element.name)
                element.name = normalized_name
                element.calling_name = normalized_name

        if type(element) is ast.TypeFunctor and not element.normalized:
            if element.name not in {'rec', 'ref', 'array'}:
                normalized_name = self.normalize_name(element.meta, element.name)
                element.name = normalized_name
                element.calling_name = normalized_name

        if type(element) is ast.SubroutineCall and not element.normalized:
            normalized_name = self.normalize_name(element.meta, element.name)
            element.name = normalized_name
            element.calling_name = normalized_name

        if type(element) is ast.UserStatementFunction and not element.normalized:
            normalized_name = self.normalize_name(element.meta, element.name)
            element.calling_name = normalized_name

        for arg in element.args:
            self.normalise(arg)

        element.normalized = True

    def get_normalised_program(self):
        self.build_head_names()
        self.normalise(self.program)
        return self.program

    def build_head_names(self):
        types = ast.MetaVar()
        global_inits = ast.MetaVar()
        defs = ast.MetaVar()
        statements = ast.MetaVar()

        ast.Program(types, global_inits, defs, statements) << self.program

        # types
        for arg in types.val.args:
            template_var = ast.MetaVar()
            type_expression = ast.MetaVar()
            extend_list = ast.MetaVar()
            ast.AssignType(template_var, type_expression, extend_list) << arg
            name = template_var.val.args[0].name
            normalized_name = self.normalize_head_name(template_var.val.meta, name)
            template_var.val.args[0].name = normalized_name
            template_var.val.args[0].normalized = True
            if normalized_name in self.keys:
                level.core.parser.code.ParseException(f"global name '{name}' can't be used as variable name in {template_var.val.meta}")
            else:
                self.keys.add(normalized_name)

        # subroutines
        for d in defs.val.args:
            if not d.method:
                name = d.name
                normalized_name = self.normalize_head_name(d.meta, name)
                d.name = normalized_name
                d.normalized = True
                if normalized_name in self.keys:
                    level.core.parser.code.ParseException(f"global name '{name}' can't be used as variable name in {d.meta}")
                else:
                    self.keys.add(normalized_name)

        # globals
        for arg in global_inits.val.args:
            var = ast.MetaVar()
            type_expression = ast.MetaVar()
            init_expression = ast.MetaVar()
            ast.InitGlobalWithType(var, type_expression, init_expression) << arg
            name = var.val.name
            normalized_name = self.normalize_head_name(var.val.meta, name)
            var.val.name = normalized_name
            var.val.calling_name = normalized_name
            var.val.normalized = True
            if normalized_name in self.keys:
                level.core.parser.code.ParseException(f"global name '{name}' can't be used as variable name in {var.val.meta}")
            else:
                self.keys.add(normalized_name)
