#!/usr/bin/env python3

# Vtoken tool by BigNerd95

import sys, os
from argparse import ArgumentParser, FileType
import struct, crcmod.predefined
jamCRC = crcmod.predefined.mkCrcFun('jamcrc')


class Vtoken():

    flashtypes = [ "", "NOR", "NAND16", "NAND128"]

    def __init__(self, fd):
        fd.seek(0, 0)
        data = fd.read()

        self.image  = data[:-20]
        self.vtoken = data[-20:]
        self.__parse__(self.vtoken)
        self.__check__(self.image)     

    def __parse__(self, data):
        (self.crc, 
        self.magic, 
        self.chip, 
        self.flashtype, 
        self.null) = struct.unpack(">LLLLL", data)

    def __check__(self, data):
        errors = []
        if self.crc != jamCRC(data):
            errors.append("CRC")
        if self.magic != 0x00005732:
            errors.append("Magic")
        if self.null  != 0x00000000:
            errors.append("Unused")

        s = "Errors on field: "
        for x in errors:
            s += x + " "

        if len(errors) > 0:
            raise Exception("Invalid vtoken!\n" + s)

    def update(self):
        self.crc = jamCRC(self.image)
        self.vtoken = struct.pack(">LLLLL", 
                        self.crc, 
                        self.magic, 
                        self.chip, 
                        self.flashtype, 
                        self.null
                    )

    def build(self):
        return self.image + self.vtoken

    def __str__(self):
        return "CRC:        " + str(hex(self.crc)) + "\n" \
               "Magic:      " + str(hex(self.magic))  + "\n" \
               "Chip ID:    " + str(hex(self.chip)[2:]) + "\n" \
               "Flash type: " + str(Vtoken.flashtypes[int(self.flashtype)]) + "\n" \
               "Unused:     " + str(hex(self.null))  + "\n"
              

##################
# main functions #
##################

def merge(input_file, custom_image, output_file):
    print("** Vtoken merge **")
    try:
        vtoken = Vtoken(input_file)
    except Exception as e:
        print("Error parsing file!")
        print(e)
        return
    finally:
        input_file.close()

    print("Original image info")
    print(vtoken)
    print()
        
    vtoken.image = custom_image.read()
    vtoken.update()

    print("Custom image info")
    print(vtoken)
    print()

    output_file.write(vtoken.build())
    print("Vtoken merged!")

    custom_image.close()
    output_file.close()

def remove(input_file, output_file):
    print("** Vtoken remove **")

    try:
        vtoken = Vtoken(input_file)
        print(vtoken)
    except Exception as e:
        print("Error parsing file!")
        print(e)
        return
    finally:
        input_file.close()

    output_file.write(vtoken.image)
    print("Vtoken removed!")

    output_file.close()

def info(input_file):
    print("** Vtoken info **")

    try:
        vtoken = Vtoken(input_file)
        print(vtoken)
    except Exception as e:
        print("Error parsing file!")
        print(e)
    finally:
        input_file.close()

def parse_cli():
    parser = ArgumentParser(description='** Vtoken Tool by BigNerd95 **')
    subparser = parser.add_subparsers(dest='subparser_name')

    infoParser = subparser.add_parser('info', help='Print vtoken info')
    infoParser.add_argument('-i', '--input', required=True, metavar='INPUT_FILE', type=FileType('rb'))

    removeParser = subparser.add_parser('remove', help='Remove vtoken from image')
    removeParser.add_argument('-i', '--input', required=True, metavar='INPUT_FILE', type=FileType('rb'))
    removeParser.add_argument('-o', '--output', required=True, metavar='OUTPUT_FILE', type=FileType('wb'))

    mergeParser = subparser.add_parser('merge', help='Create a new file with custom image and original vtoken')
    mergeParser.add_argument('-i', '--input',  required=True, metavar='INPUT_FILE', type=FileType('rb'))
    mergeParser.add_argument('-c', '--custom', required=True, metavar='CUSTOM_IMAGE', type=FileType('rb'))
    mergeParser.add_argument('-o', '--output', required=True, metavar='OUTPUT_FILE', type=FileType('wb'))

    if len(sys.argv) < 2:
        parser.print_help()

    return parser.parse_args()

def main():
    args = parse_cli()
    if args.subparser_name == 'info':
        info(args.input)
    elif args.subparser_name == 'remove':
        remove(args.input, args.output)
    elif args.subparser_name == 'merge':
        merge(args.input, args.custom, args.output)

if __name__ == '__main__':
    main()
