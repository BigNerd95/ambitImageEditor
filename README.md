# ambitImageEditor
Ambit Image Editor tool

With this tool you can edit official firmwares of some modem router (like Netgear) created by "packet" executable.  
This tool can change the kernel and the file system of an official firmware.  

My work is based on tools provided in the [GPL](https://www.downloads.netgear.com/files/GPL/DGN2200v4_V1.0.0.98_1.0.98_src_full.zip) archive of DGN2200v4.  

## Usage
### Info  
Show firmware image info    
`./ambitImageEditor.py info -i DGN2200v4.chk`

### Split  
Extract rootfs and kernel from a firmware image     
`./ambitImageEditor.py split -i DGN2200v4.chk -d extract`

### Merge
Create a new firmware image with custom rootfs and kernel     
`./ambitImageEditor.py merge -i DGN2200v4.chk -o Custom2200v4.chk -r extract/rootfs -k extract/kernel`

## Examples
You can find a guide about creating a custom firmware [here](GUIDE.md)

## Firmware structure
| Size (byte)  | Name | Description |
| :----------: | ---- | ------- |
| 40-240 | Ambit header | Described below (variable size, specified in size field) |
| RootFS Size in Header | Root File System | SquashFS, CramFS or Jffs2 |
| Kernel Size in Header | Kernel | LZMA compressed kernel |

## Ambit header structure
| Size (byte)  | Type | Name | Description |
| :----------: | ---- | ---- | ------- |
| 4 | Char | Magic | Content: *#$^ |
| 4 | Unsigned BE Int 32 | Header size | From Magic to Board ID included. Minimim size: 40, Maximum size: 240 (due to Board ID field) |
| 1 | Unsigned BE Int  8 | Region Index | See Firmware regions below |
| 4 | Unsigned BE Int  8 | SW version | Eg: 1.0.0.98 |
| 3 | Unsigned BE Int  8 | UI version | Eg: 1.0.98 |
| 4 | Unsigned BE Int 32 | Kernel checksum | Variant of Fletcher 32 checksum |
| 4 | Unsigned BE Int 32 | RootFS checksum | Variant of Fletcher 32 checksum |
| 4 | Unsigned BE Int 32 | Kernel size | CFE starting address (if non zero) |
| 4 | Unsigned BE Int 32 | RootFS size | CFE size in clear ASCII text (if non zero) |
| 4 | Unsigned BE Int 32 | RootFS + Kernel checksum | Variant of Fletcher 32 checksum |
| 4 | Unsigned BE Int 32 | Header checksum | Variant of Fletcher 32 checksum (with this field set to 0, Board ID included) |
| 0-200 | String | Board ID | Eg: U12L227T01_NETGEAR |

### Firmware regions
| Index | Value |
| :---: | ----- |
| 0 | NONE_VERSION | 
| 1 | WW_VERSION |
| 2 | NA_VERSION |
| 3 | JP_VERSION |   
| 4 | GR_VERSION |  
| 5 | PR_VERSION |
| 6 | KO_VERSION |   
| 7 | RU_VERSION |  
| 8 | SS_VERSION |
| 9 | PT_VERSION |   
| 10| TWC_VERSION | 
| 11| BRIC_VERSION |
| 12| SK_VERSION |

## Dependences
- crcmod  
- struct  
- argparse  
- construct  

(Install them with `pip3`)
