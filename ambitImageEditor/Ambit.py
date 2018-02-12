#!/usr/bin/env python3

# Ambit lib by BigNerd95

from construct import *

# Ambit constants
FIXED_HEADER_LEN = 40
MAX_HEADER_SIZE  = FIXED_HEADER_LEN + 200

regions = [ "NONE_VERSION", "WW_VERSION",  "NA_VERSION",
            "JP_VERSION",   "GR_VERSION",  "PR_VERSION",
            "KO_VERSION",   "RU_VERSION",  "SS_VERSION",
            "PT_VERSION",   "TWC_VERSION", "BRIC_VERSION",
            "SK_VERSION" ]

ambitHeader = Struct(
    "magic"  / Const(b"*#$^"),
    "size"   / Int32ub,
    "fw_region_index" / Int8ub,
    "sw_version" / Array(4, Byte),
    "ui_version" / Array(3, Byte),
    "kernel_checksum" / Int32ub,
    "rootfs_checksum" / Int32ub,
    "kernel_size" / Int32ub,
    "rootfs_size" / Int32ub,
    "rootfs_kernel_checksum" / Int32ub,
    "header_checksum" / Int32ub,
    "board_id" / String(this.size - FIXED_HEADER_LEN, StringsAsBytes),
)

class Image():
    def __init__(self, fd):
        fd.seek(0, 0)
        self.values = ambitHeader.parse(fd.read(MAX_HEADER_SIZE))

        # get RootFS from file
        fd.seek(self.values.size, 0)
        self.rootfs = fd.read(self.values.rootfs_size)

        # get Kernel from file
        fd.seek(self.values.size + self.values.rootfs_size)
        self.kernel = fd.read(self.values.kernel_size)


    def __header_checksum__(self):
        self.values.header_checksum = 0
        return checksum(self.makeHeader())

    def __update_sizes__(self):
        # update sizes
        self.values.size = FIXED_HEADER_LEN + len(self.values.board_id)
        self.values.rootfs_size = len(self.rootfs)
        self.values.kernel_size = len(self.kernel)

    def __update_checksums__(self):
        # update checksums
        self.values.rootfs_checksum = checksum(self.rootfs)
        self.values.kernel_checksum = checksum(self.kernel)
        self.values.rootfs_kernel_checksum = checksum(self.rootfs + self.kernel)
        self.values.header_checksum = self.__header_checksum__() # must be the latest to be updated!!!

    def update(self):
        self.__update_sizes__()
        self.__update_checksums__()

    # build header updating all correlated values
    def makeUpdateHeader(self):
        self.update()
        return self.makeHeader()

    # build the header as is
    def makeHeader(self):
        return ambitHeader.build(self.values)

    # build entire image updating all correlated values
    def makeUpdateImage(self):
        return self.makeUpdateHeader() + self.rootfs + self.kernel

    # build entire image as is
    def makeImage(self):
        return self.makeHeader() + self.rootfs + self.kernel

    def __str__(self):
        return "FW region:  " + str(regions[self.values.fw_region_index])  + "\n" \
               "SW version: " + ".".join(map(str, self.values.sw_version)) + "\n" \
               "UI version: " + ".".join(map(str, self.values.ui_version)) + "\n" \
               "Board ID:   " + str(self.values.board_id.decode("ascii"))  + "\n" \
               "Sizes:\n" + \
               "\tHeader: " + str(self.values.size)         + " bytes\n" \
               "\tRootFS: " + str(self.values.rootfs_size)  + " bytes\n" \
               "\tKernel: " + str(self.values.kernel_size)  + " bytes\n" \
               "Checksums:\n" + \
               "\tHeader:          " + str(hex(self.values.header_checksum))         + "\n" \
               "\tRootFS:          " + str(hex(self.values.rootfs_checksum))         + "\n" \
               "\tKernel:          " + str(hex(self.values.kernel_checksum))         + "\n" \
               "\tRootFS + Kernel: " + str(hex(self.values.rootfs_kernel_checksum))  + "\n"

# Fletcher-32 checksum
def checksum(data):
    adder0 = adder1 = 0

    for b in data:
        adder0 += b
        adder1 += adder0

    adder0 &= 0xFFFFFFFF
    adder1 &= 0xFFFFFFFF

    adder0 = (adder0  + (adder0 >> 16) + (((adder0 & 0xFFFF) + (adder0 >> 16)) >> 16)) & 0xFFFF
    adder1 = (adder1  + (adder1 >> 16) + (((adder1 & 0xFFFF) + (adder1 >> 16)) >> 16)) & 0xFFFF

    return (adder1 << 16) | adder0

# test function
# python3 Ambit.py Firmware.chk
if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "rb") as f:
        ambit = Image(f)

        print("Raw detailed print")
        print(ambit.values)
        print()

        print("Info print")
        print(ambit)
        print()

        print("Checksum test")
        print("\tHeader checksum")
        print("\t\tHeader value:  ", hex(ambit.values.header_checksum))
        ambit.makeHeader() # make method recompute the header checksum!
        print("\t\tComputed value:", hex(ambit.values.header_checksum)) # so its right to read again the checksum from the header

        print("\tRootfs checksum")
        print("\t\tHeader value:  ", hex(ambit.values.rootfs_checksum))
        f.seek(ambit.values.size, 0)
        rootfs = f.read(ambit.values.rootfs_checksum)
        print("\t\tComputed value:", hex(checksum(rootfs)))

        print("\tKernel checksum")
        print("\t\tHeader value:  ", hex(ambit.values.kernel_checksum))
        f.seek(ambit.values.size + ambit.values.rootfs_size, 0)
        kernel = f.read(ambit.values.kernel_size)
        print("\t\tComputed value:", hex(checksum(kernel)))

        print("\tRootfs + Kernel checksum")
        print("\t\tHeader value:  ", hex(ambit.values.rootfs_kernel_checksum))
        f.seek(ambit.values.size, 0)
        rootfs_kernel = f.read(ambit.values.kernel_size + ambit.values.rootfs_checksum)
        print("\t\tComputed value:", hex(checksum(rootfs_kernel)))
