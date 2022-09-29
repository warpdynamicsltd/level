import os
import re


import level.core.parser.code
from level.install import modules
from level.core.parser.normalizer import Imports, ImportItem
from level.core.parser.builtin import default_modules

class LinkerException(Exception):
    pass

class Linker:
    def __init__(self):
        level.core.parser.code.MetaParserInfo.module_map = {}
        self.imports = Imports()
        self.chars = []

        self.loaded = set()
        self.processed_modules = set()

    def find_file(self, s):
        segment = s.split(':')
        segment[-1] += '.lvl'
        for p in modules():
            filename = os.path.join(p, *segment)
            if os.path.isfile(filename):
                return filename

        return None

    def count_nc(self, s):
        line_n = 0
        char_n = 0
        for c in s:
            char_n += 1

            if c == '\n':
                line_n += 1
                char_n = 1

        return line_n, char_n


    def file_to_alphabet_characters(self, filename, module_name=None):
        with open(filename, "rb") as f:
            raw = f.read()
            text = str(raw, encoding='utf-8')
            self.text_recursive(text, module_name)

    def text_recursive(self, text, module_name):
        if module_name is None:
            module_name = 'main'
        if module_name in self.processed_modules:
            return
        line_n = 1
        char_n = 1
        dict_module_alias = {}
        if module_name == "main":
            for imported_module_name, alias in default_modules:
                dict_module_alias[imported_module_name] = alias

        while True:
            m = re.match(r"^\s*import\s+(?P<lead>[_a-zA-Z0-9:]+)(\s+as\s+(?P<as>([_a-zA-Z0-9:]+|\*)))?\s*;", text, re.MULTILINE)
            if m:
                i, j = m.span()
                imported_module_name, alias = m.group('lead'), m.group('as')

                if alias is None:
                    alias = imported_module_name
                if alias == '*':
                    alias = None

                if imported_module_name in dict_module_alias:
                    raise LinkerException(f"module {imported_module_name} already imported in {module_name}")

                dict_module_alias[imported_module_name] = alias
            else:
                m = re.match(r"^\s*#.*\n", text)
                if m:
                    i, j = m.span()
                else:
                    break

            line_n_, char_n_ = self.count_nc(text[i:j])
            line_n += line_n_
            char_n += char_n_
            text = text[j:]

        for imported_module_name in dict_module_alias:
            alias = dict_module_alias[imported_module_name]
            self.imports.add_import_item(
                source_module=module_name,
                import_item=ImportItem(
                    module_name=imported_module_name,
                    alias=alias))
            filename = self.find_file(imported_module_name)
            if filename is not None:
                self.file_to_alphabet_characters(filename, imported_module_name)
            else:
                raise LinkerException(f"can't import {imported_module_name} in {module_name}")

        self.text_to_alphabet_characters(text, module_name, line_n, char_n)
        self.processed_modules.add(module_name)


    def text_to_alphabet_characters(self, text, module_name, line_n=1, char_n=1):
        module_code = hash(module_name)
        if module_code not in level.core.parser.code.MetaParserInfo.module_map:
            level.core.parser.code.MetaParserInfo.module_map[module_code] = module_name

        for c in text:
            self.chars.append(level.core.parser.code.Char(c, meta=level.core.parser.code.MetaParserInfo(line_n, char_n, module_code)))

            char_n += 1

            if c == '\n':
                line_n += 1
                char_n = 1
