projectFolder=$(pwd)/../
firmware=$1

$projectFolder/ambitImageEditor/ambitImageEditor.py split -i ${firmware} -d ${firmware}_extract
$projectFolder/vtoken/vtoken.py remove -i ${firmware}_extract/kernel -o ${firmware}_extract/kernel.clean
sudo binwalk -e ${firmware}_extract/kernel.clean -C ${firmware}_extract

echo "Make your changes!"
read

$projectFolder/tools/mkfs.jffs2 -b -p -n -e 16384 -r ${firmware}_extract/_kernel.clean.extracted/jffs2-root/fs_1 -o ${firmware}_extract/kernel.new.clean -N $projectFolder/tools/nocomprlist
$projectFolder/vtoken/vtoken.py merge -i ${firmware}_extract/kernel -c ${firmware}_extract/kernel.new.clean -o ${firmware}_extract/kernel.new
$projectFolder/ambitImageEditor/ambitImageEditor.py merge -i ${firmware} -o ${firmware}_custom.chk -k ${firmware}_extract/kernel.new -r ${firmware}_extract/rootfs

