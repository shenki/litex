import csv


class CSRElements:
    def __init__(self, d):
        self.d = d

    def __getattr__(self, attr):
        try:
            return self.__dict__['d'][attr]
        except KeyError:
            pass
        raise KeyError("No such element " + attr)


class CSRRegister:
    def __init__(self, readfn, writefn, name, addr, length, data_width, mode):
        self.readfn = readfn
        self.writefn = writefn
        self.name = name
        self.addr = addr
        self.length = length
        self.data_width = data_width
        self.mode = mode

    def read(self):
        if self.mode not in ["rw", "ro"]:
            raise KeyError(self.name + "register not readable")
        datas = self.readfn(self.addr, length=self.length)
        if isinstance(datas, int):
            return datas
        else:
            data = 0
            for i in range(self.length):
                data = data << self.data_width
                data |= datas[i]
            return data

    def write(self, value):
        if self.mode not in ["rw", "wo"]:
            raise KeyError(self.name + "register not writable")
        datas = []
        for i in range(self.length):
            datas.append((value >> ((self.length-1-i)*self.data_width)) & (2**self.data_width-1))
        self.writefn(self.addr, datas)


class CSRMemoryRegion:
    def __init__(self, base, size):
        self.base = base
        self.size = size


class CSRBuilder:
    def __init__(self, comm, csr_csv, csr_data_width):
        self.csr_data_width = csr_data_width
        self.constants = self.build_constants(csr_csv)
        self.bases = self.build_bases(csr_csv)
        self.regs = self.build_registers(csr_csv, comm.read, comm.write)
        self.mems = self.build_memories(csr_csv)

    def build_bases(self, csr_csv):
        csv_reader = csv.reader(open(csr_csv), delimiter=',', quotechar='#')
        d = {}
        for item in csv_reader:
            group, name, addr, dummy0, dummy1 = item
            if group == "csr_base":
                d[name] = int(addr.replace("0x", ""), 16)
        return CSRElements(d)

    def build_registers(self, csr_csv, readfn, writefn):
        csv_reader = csv.reader(open(csr_csv), delimiter=',', quotechar='#')
        d = {}
        for item in csv_reader:
            group, name, addr, length, mode = item
            if group == "csr_register":
                addr = int(addr.replace("0x", ""), 16)
                length = int(length)
                d[name] = CSRRegister(readfn, writefn, name, addr, length, self.csr_data_width, mode)
        return CSRElements(d)

    def build_constants(self, csr_csv):
        csv_reader = csv.reader(open(csr_csv), delimiter=',', quotechar='#')
        d = {}
        for item in csv_reader:
            group, name, value, dummy0, dummy1 = item
            if group == "constant":
                try:
                    d[name] = int(value)
                except:
                    d[name] = value
        return CSRElements(d)

    def build_memories(self, csr_csv):
        csv_reader = csv.reader(open(csr_csv), delimiter=',', quotechar='#')
        d = {}
        for item in csv_reader:
            group, name, base, size, dummy1 = item
            if group == "memory_region":
                d[name] = CSRMemoryRegion(int(base, 16), int(size))
        return CSRElements(d)
