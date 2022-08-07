import os
import re
import hashlib

import level.core.parser.code
from level.install import modules

class LinkerException(Exception):
    pass

class Lead:
    def __init__(self, key, name):
        self.key = key
        self.name = name

class Linker:
    def __init__(self):
        self.chars = []

        self.loaded = set()

    def find_file(self, s):
        # print(s)
        segment = s.split(':')
        segment[-1] += '.lvl'
        for p in modules():
            filename = os.path.join(p, *segment)
            # print(filename)
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


    def file_to_alphabet_characters(self, filename, lead=None, module_name=None):
        with open(filename, "rb") as f:
            raw = f.read()
            # h = hashlib.sha256(raw).digest()
            #
            # if h in self.loaded:
            #     return
            # self.loaded.add(h)

            text = str(raw, encoding='utf-8')
            self.text_recursive(text, lead, module_name)

    def text_recursive(self, text, lead, module_name):
        line_n = 1
        char_n = 1
        while True:
            m = re.match(r"^\s*import\s+(?P<lead>[_a-zA-Z0-9:]+)(\s+as\s+(?P<as>([_a-zA-Z0-9:]+|\*)))?\s*;", text, re.MULTILINE)
            if m:
                i, j = m.span()
                module_lead = Lead(m.group('lead'), m.group('as'))
                filename = self.find_file(module_lead.key)
                if filename is not None:
                    if lead is None:
                    # we are in root document
                        if module_lead.name is None:
                            child_lead = Lead(key=module_lead.key, name=module_lead.key)
                        else:
                            if module_lead.name == '*':
                                child_lead = None
                                #child_lead = Lead(key=module_lead.key, name=0)
                            else:
                                child_lead = Lead(key=module_lead.key, name=module_lead.name)
                    else:
                        if module_lead.name is None:
                            child_lead = Lead(key=f"{module_lead.key}", name=f"{lead.name}:{module_lead.key}")
                        else:
                            if module_lead.name == '*':
                                child_lead = Lead(key=f"{module_lead.key}", name=f"{lead.name}")
                            else:
                                child_lead = Lead(key=f"{module_lead.key}", name=f"{lead.name}:{module_lead.name}")


                    self.file_to_alphabet_characters(filename, child_lead, module_lead.key)
                else:
                    if lead is None:
                        lead = Lead(key="main", name=None)
                    raise LinkerException(f"can't import {module_lead.key} in {lead.key}")
                line_n_, char_n_ = self.count_nc(text[i:j])
                line_n += line_n_
                char_n += char_n_
                text = text[j:]
            else:
                break

        self.text_to_alphabet_characters(text, lead, module_name, line_n, char_n)


    def text_to_alphabet_characters(self, text, lead, module_name, line_n=1, char_n=1):
        for c in text:
            self.chars.append(level.core.parser.code.Char(c, meta=level.core.parser.code.MetaParserInfo(line_n, char_n, lead, module_name)))

            char_n += 1

            if c == '\n':
                line_n += 1
                char_n = 1
