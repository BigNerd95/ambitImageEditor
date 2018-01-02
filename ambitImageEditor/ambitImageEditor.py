#!/usr/bin/env python3

# Ambit Image Editor by BigNerd95

import sys, os, Ambit
from argparse import ArgumentParser, FileType

def create_write_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)

##################
# main functions #
##################

def merge(input_file, custom_rootfs_file, custom_kernel_file, output_file):
    print("** Ambit Image merge **")
    print("Parsing file...\n")
    try:
        ambitImage = Ambit.Image(input_file)
    except Exception as e:
        print("Error parsing file!")
        print(e)
        print("Be sure to pass a CHK file!")
        return
    finally:
        input_file.close()

    print("Original firmware info")
    print(ambitImage)
    print()

    print("Merging image...\n")
    ambitImage.rootfs = custom_rootfs_file.read()
    ambitImage.kernel = custom_kernel_file.read()
    ambitImage.update()

    print("Custom firmware info")
    print(ambitImage)
    print()

    print("Writing custom image...")
    output_file.write(ambitImage.makeImage())

    print("Done!")
    custom_rootfs_file.close()
    custom_kernel_file.close()
    output_file.close()

def split(input_file, directory):
    print("** Ambit Image split **")
    print("Parsing file...")

    try:
        ambitImage = Ambit.Image(input_file)
    except Exception as e:
        print("Error parsing file!")
        print(e)
        print("Be sure to pass a CHK file!")
        return
    finally:
        input_file.close()

    print("Creating directory:", directory)
    path = os.path.join(directory, '')
    if os.path.exists(path):
        print("Directory", os.path.basename(path) , "already exists, cannot split!")
        return

    print("Extracting RootFS...")
    create_write_file(path + 'rootfs', ambitImage.rootfs)
    print("Extracting Kernel...")
    create_write_file(path + 'kernel', ambitImage.kernel)

    print("Done!")


def info(input_file):
    print("** Ambit Image info **")

    print("Parsing file...")
    try:
        ambitImage = Ambit.Image(input_file)
        print(ambitImage)
    except Exception as e:
        print("Error parsing file!")
        print(e)
        print("Be sure to pass a CHK file!")
    finally:
        input_file.close()

def parse_cli():
    parser = ArgumentParser(description='** Ambit Image Editor by BigNerd95 **')
    subparser = parser.add_subparsers(dest='subparser_name')

    infoParser = subparser.add_parser('info', help='Print Image (header) info')
    infoParser.add_argument('-i', '--input', required=True, metavar='INPUT_FILE', type=FileType('rb'))

    splitParser = subparser.add_parser('split', help='Extract rootfs and kernel from image')
    splitParser.add_argument('-i', '--input', required=True, metavar='INPUT_FILE', type=FileType('rb'))
    splitParser.add_argument('-d', '--directory', required=True, metavar='EXTRACT_DIRECTORY')

    mergeParser = subparser.add_parser('merge', help='Create a new image with custom rootfs and kernel using the original image as base')
    mergeParser.add_argument('-i', '--input',  required=True, metavar='INPUT_FILE', type=FileType('rb'))
    mergeParser.add_argument('-r', '--rootfs', required=True, metavar='ROOTFS_FILE', type=FileType('rb'))
    mergeParser.add_argument('-k', '--kernel', required=True, metavar='KERNEL_FILE', type=FileType('rb'))
    mergeParser.add_argument('-o', '--output', required=True, metavar='OUTPUT_FILE', type=FileType('wb'))

    if len(sys.argv) < 2:
        parser.print_help()

    return parser.parse_args()

def main():
    args = parse_cli()
    if args.subparser_name == 'info':
        info(args.input)
    elif args.subparser_name == 'split':
        split(args.input, args.directory)
    elif args.subparser_name == 'merge':
        merge(args.input, args.rootfs, args.kernel, args.output)

if __name__ == '__main__':
    main()
