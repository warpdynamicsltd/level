from level.utils.binparse import *


class ELF64(BinParse):
    """
    The .text section is always at 0x80 offset. It seems that this makes possible
    entrypoint is a form of k*0x10000 + 0x80 (investigate why - it looks like
    whole ELF is loaded to virtual memory from k*0x10000.

    The .data section must be after .text section can't have offset greater that k*0x10000 + 0x10000
    (investigate why)
    """
    def __init__(self,
                 block,
                 offset=0,
                 endianness=BinParse.LITTLE_ENDIAN,
                 text_payload=bytes(),
                 text_offset=0x400080,
                 entry=0x400080,
                 n_segments=1,
                 segment_size=0x1000000,
                 mode=BinParse.PASSIVE):
        self.text_payload = text_payload
        #self.data_payload = data_payload
        self.text_offset = text_offset
        #self.data_offset = data_offset
        self.entry = entry
        self.n_segments = n_segments
        self.segment_size = segment_size
        meta = self
        BinParse.__init__(self, block, offset, endianness, mode, meta)

    class ELFHeader(BinParse):
        def build(self):
            self.add_array('e_ident', UINT8, 16)

            if self.mode == BinParse.ACTIVE:
                self.e_ident[4] = 2  # 64 bit
                self.e_ident[5] = 1 if self.endianness == BinParse.LITTLE_ENDIAN else 2
            else:
                if self.e_ident[4] != 2:
                    raise BinParseException("ELF64 parse error")
                self.endianness = BinParse.LITTLE_ENDIAN if self.e_ident[5] == 1 else BinParse.BIG_ENDIAN

            self.add('e_type', UINT16)
            self.add('e_machine', UINT16)
            self.add('e_version', UINT32)
            self.add('e_entry', UINT64)
            self.add('e_phoff', UINT64)
            self.add('e_shoff', UINT64)
            self.add('e_flags', UINT32)
            self.add('e_ehsize', UINT16)
            self.add('e_phentsize', UINT16)
            self.add('e_phnum', UINT16)
            self.add('e_shentsize', UINT16)
            self.add('e_shnum', UINT16)
            self.add('e_shstrndx', UINT16)

            if self.mode == BinParse.ACTIVE:
                self.e_ehsize = 64
                self.e_shnum = 3
                self.e_shstrndx = 2

                self.e_ident = [127, 69, 76, 70, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                self.e_type = 0x2  # Executable file
                self.e_machine = 0x3e  # AMD x86-64
                self.e_version = 0x01  #
                self.e_entry = self.meta.entry # self.meta.text_offset
                self.e_flags = 0x0
                self.e_phentsize = 56
                self.e_shentsize = 64

    class ELFProgramHeader(BinParse):
        def build(self):
            #print('**')
            self.add('p_type', UINT32)
            self.add('p_flags', UINT32)
            self.add('p_offset', UINT64)
            self.add('p_vaddr', UINT64)
            self.add('p_paddr', UINT64)
            self.add('p_filesz', UINT64)
            self.add('p_memsz', UINT64)
            self.add('p_align', UINT64)

            if self.mode == BinParse.ACTIVE:
                self.p_type = 1  # Loadable segment
                self.p_flags = (0x1 | 0x2 | 0x4)  # ewr
                self.p_vaddr = self.meta.text_offset
                self.p_paddr = self.meta.text_offset  # physical address
                self.p_filesz = self.meta.segment_size
                self.p_memsz = self.meta.segment_size
                self.p_align = 0x10

            else:
                if self.p_type != 1:
                    raise BinParseException("ELF64 parse error")

    class ELFSectionHeader(BinParse):
        def build(self):
            self.add('sh_rel_name', UINT32)
            self.add('sh_type', UINT32)
            self.add('sh_flags', UINT64)
            self.add('sh_addr', UINT64)
            self.add('sh_offset', UINT64)
            self.add('sh_size', UINT64)
            self.add('sh_link', UINT32)
            self.add('sh_info', UINT32)
            self.add('sh_addralign', UINT64)
            self.add('sh_entsize', UINT64)

            if self.mode == BinParse.ACTIVE:
                pass

    def build(self):
        self.add('header', ELF64.ELFHeader)

        if self.mode == BinParse.ACTIVE:
            self.header.e_phoff = self.header.e_ehsize
            self.header.e_phnum = self.meta.n_segments

        self.add_array('program_header_table', ELF64.ELFProgramHeader, self.header.e_phnum)

        if self.mode == BinParse.ACTIVE:
            self.align(0x10)
            self.program_header_table[0].p_offset = self.cursor
            p_offset = self.cursor
            mem_offset = self.text_offset
            for i in range(0, int(self.header.e_phnum)):
                self.program_header_table[i].p_offset = p_offset
                self.program_header_table[i].p_vaddr = mem_offset

                p_offset += int(self.program_header_table[i].p_filesz)
                mem_offset += int(self.program_header_table[i].p_memsz)

            self.add_array('text', BYTE, len(self.meta.text_payload))
            self.text = self.meta.text_payload
            payload = b"\x00.text\x00.shstrtab\x00"
            self.align(0x10)
            self.add_array('shstrtab', BYTE, len(payload))
            self.shstrtab = payload
            self.header.e_shoff = self.cursor
        #
        if self.mode == BinParse.ACTIVE:
            self.add_array('section_header_table', ELF64.ELFSectionHeader, self.header.e_shnum)
        else:
            self.reg_array('section_header_table', ELF64.ELFSectionHeader, self.header.e_shnum, offset=self.header.e_shoff)

        if self.mode == BinParse.ACTIVE:
            text_header = self.section_header_table[1]
            shstrtab_header = self.section_header_table[2]

            text_header.sh_offset = self.text.offset
            text_header.sh_size = self.text.size
            text_header.sh_rel_name = payload.find(b".text")

            text_header.sh_type = 0x1  # Program data
            text_header.sh_flags = (0x1 | 0x2 | 0x4)  # Writable | Allocated | Executable
            text_header.sh_addr = self.meta.text_offset
            text_header.sh_link = 0x0
            text_header.sh_info = 0x0
            text_header.sh_addralign = 0x10
            text_header.sh_entsize = 0x0

            shstrtab_header.sh_offset = self.shstrtab.offset
            shstrtab_header.sh_size = self.shstrtab.size
            shstrtab_header.sh_rel_name = payload.find(b".shstrtab")

            shstrtab_header.sh_type = 0x3  # String table
            shstrtab_header.sh_flags = 0x0
            shstrtab_header.sh_addr = 0x0
            shstrtab_header.sh_link = 0x0
            shstrtab_header.sh_info = 0x0
            shstrtab_header.sh_addralign = 0x1
            shstrtab_header.sh_entsize = 0x0

        for i in range(0, int(self.header.e_shnum)):
            sh_header = self.section_header_table[i]
            sh_header.reg(
                'sh_name',
                SZ,
                offset=self.section_header_table[self.header.e_shstrndx].sh_offset + sh_header.sh_rel_name
            )

            sh_header.reg_array(
                'sh_bytes',
                BYTE,
                length=self.section_header_table[i].sh_size,
                offset=self.section_header_table[i].sh_offset
            )

        if self.mode == BinParse.ACTIVE:
            text_header.sh_name = ".text"
            shstrtab_header.sh_name = ".shstrtab"
