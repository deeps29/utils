"""
Script to archive RAW files into several sub folders using metadata in file names.
It reads focal length, data and time of the capture, exposure time, aperture and iso speed used.
It also extracts Camera Temperature but only Canon cameras support that, in case of Nikon, it will use x as temperature value

This program need to call ExifTool by Phil Harvey which you can download here:
https://exiftool.org
Supported RAW formats: CR2, CR3 and NEF
To run the script -
python3 /Users/deepanshu/Desktop/TSE2024/sorter.py --path /Users/deepanshu/Desktop/ecl2024/partials_tests4 --camera-prefix ASR5

Usage:
    sorter.py [--path] [--camera-prefix]
    --path : provide absolute path
    --camera-prefix : provide camera name you want to use in file name
    --subfolder : If used, script will create subfolder using exposure time and iso speed as names

Author: Deepanhu Arora
Licensed under GPL v3
"""

import argparse
import sys
import string
import os
import subprocess
import time
import platform

# Input arguments
parser = argparse.ArgumentParser(
        description='This script reads exif data from camera raw and renames the files with more descriptive names.',
        prog='sorter'
    )
parser.add_argument('-v', '--version', action='version', version='%(prog)s v1.0')
parser.add_argument(
    '--path',
    type=str,
    required=True,
    help='Path to the input directory, can read CR2, CR3 and NEF.'
)
parser.add_argument(
    '--subfolder',
    type=bool,
    required=False,
    default=False,
    help='If True, moves the files to subfolders.'
)
parser.add_argument(
    '--camera-prefix',
    type=str,
    required=True,
    help='Camera name prefix required.'
)
args, unparsed = parser.parse_known_args()

FORMATDICT = {1:['.cr2', '.CR2'], 2:['.cr3', '.CR3'], 3:['.nef', '.NEF'], 4:['.dng', '.DNG'], 5:['.cr3', '.CR3', '.nef', '.NEF', '.cr2', '.CR2']}
FILEFORMAT = FORMATDICT[5]

pltfrm = platform.system()

## change the rational string to a float (unused)
def rational2float(s):
    try:
        return format(float(s), '0.6f')
    except ValueError:
        num, denom = s.split('/')
        return format(float(num) / float(denom), '0.6f')

## change the rational string to a filename friendly string
def rational2fnfs(s):
    try:
        return s.replace('/', 'o')
    except ValueError:
        return s

# Get the list of prefered RAW files from the specified directory.
start_wd = os.getcwd() ## storing current path in a variable in case if it is needed later
os.chdir(args.path)
filelist = os.listdir('.')
rawfiles = []
for files in filelist:
    if os.path.getsize(files) == 0:
        continue
    if os.path.splitext(files)[1] in FILEFORMAT:
        rawfiles.append(files)

# Store file metadata to a map
newfilenames=dict()
print('Reading EXIF:.',)

if pltfrm=='Windows':
    cmd='.\exiftool.exe'
else:
    cmd = 'exiftool '

for rawfile in rawfiles:
    #sys.stdout.write('.')
    sys.stdout.flush()
    output = subprocess.Popen(cmd + '-FocalLength -DateTimeOriginal -ExposureTime -FNumber -ISO -CameraTemperature -T ' + rawfile, shell=True, stdout=subprocess.PIPE)
    file_metadata = output.stdout.read().decode("utf-8").split()
    file_metadata.remove('mm') #remove the mm string from the list
    try:                            # since Nikon cameras do not provide temperature values
        file_metadata.remove('C')  #remove the C string from the list for Canon
    except:
        file_metadata = list(map(lambda x: x.replace('-', 'x'), file_metadata))
    ###==================================
    # # file_metadata contents example -
    ###----------------------------------
    #     # [0] 500.0
    #     # [1] 2024:04:08
    #     # [2] 12:30:01
    #     # [3] 1/60
    #     # [4] 7.1
    #     # [5] 100
    #     # [6] 39          << -- Nikon cameras does not provide temperature value
    ###==================================
    name_prefix = 'TSE_' + args.camera_prefix
    focal_length = str(int(float(file_metadata[0]))) + 'mm'
    date_time = file_metadata[1].replace(':' , '-') + '_' + file_metadata[2].replace(':' , '-')
    exposure = str(rational2float(file_metadata[3])) + 's'
    #exposure = rational2fnfs(file_metadata[3]) + 's'
    aperture = 'f' + file_metadata[4]
    iso  = 'ISO' + file_metadata[5]
    cameraTemp = file_metadata[6] + 'C'
    name_suffix = rawfile.split('_')[-1]
    newname = name_prefix + '_' + focal_length + '_' + date_time + '_' + exposure + '_' + aperture + '_' + iso + '_' + cameraTemp + '_' + name_suffix
    print(rawfile)
    print(newname)
    print('----------------------------------------')

    if args.subfolder is True:
        subfolder_name = exposure + '_' + iso
        if not os.path.isdir(subfolder_name):
            os.mkdir(subfolder_name)
        os.rename(rawfile, subfolder_name + '/' + newname)
    else:
        os.rename(rawfile, newname)

print('Done reading EXIF')
