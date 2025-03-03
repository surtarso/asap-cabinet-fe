<h1 align="center">As Simple As Possible Cabinet Front-End</h1>

<p align="center">A dual monitor <a href="https://github.com/vpinball/vpinball">VPinballX</a> front-end for your virtual pinball cabinet.</p>
<p align="center"><i>"As Simple As Possible".</i></p>

<div align="center">
  <video src="https://github.com/user-attachments/assets/f376adfc-9481-4237-b67c-2585570cee4c" width="400" />
</div>

## Features:
- Full screen dual monitor display of table playfield, backglass and DMD
- Navigate tables with titles and wheels
- Extended settings for many display configurations
- Extremely lightweight and simple
- No need to download artpacks, generate your own!*
- Just what it takes to make a cabinet look good

*Playfield and Backglass from automated screenshots. Wheel and DMD generation not implemented yet.

## Installation:

- Download: `git clone https://github.com/surtarso/asap-cabinet-fe.git && cd asap-cabinet-fe/`

- Dependencies: `sudo apt install python3 python3-pyqt5`

- X11: `python3 asap-cabinet-fe.py`

- Wayland: `./launch.sh` (or `QT_QPA_PLATFORM=xcb python3 asap-cabinet-fe.py`)

## Using the 'screenshot_art_generator.sh' tool:

This script expects you to organize your tables by folders.
e.g. **/path/to/tables/<my_table>/<table_name.vpx>**

It will scan your tables folder and open each table one by one, wait 12 seconds for the table to fully load and take a screenshot from both app screens (playfield and backglass).

It will than save those pictures in **tables/my_table/images/** as .png and they will be ready for the frontend to display. You still need to download the wheel images and DMD animated gifs yourself.

- Dependencies: `sudo apt install xdotool imagemagick`

- Edit the screenshot_art script and set your paths.

- Dry-run to check results: `./screenshot_art_generator.sh --dry-run`

- Run the main script: `./screenshot_art_generator.sh`

**screenshot_art_generator.sh flags:** 

    no argument     Generate playfield and backglass missing images (default)
    --dry-run       Show what would be done without making changes
    --wheel         List tables missing wheel.png image and exit
    --marquee       List tables missing marquee.png image and exit
    --dmd           List tables missing dmd.gif video and exit
    --force         Recreate screenshots even if they already exist
  
    -h, --help    Show this help message and exit

## Using the 'convert_video_to_gif.sh' tool:

This script will convert all **MP4, WMV and F4V** DMD videos to **animated Gif's** so they can be displayed with this frontend (in tables/<table_name>/**images/dmd.gif**) or to play tables with Ultra.DMD videos in VPinballX-Linux.

Dependencies: `sudo apt install ffmpeg gifsicle`

Usage: `./convert_video_to_gif.sh`

**convert_video_to_gif.sh flags:**

    --now            Convert videos and optimize gifs in the current folder
    --path [dir]     Convert videos and optimize gifs in a specific directory
    --optimize       Only optimize existing GIFs in the current folder
    --optimize [dir] Only optimize existing GIFs in a specified directory

## Roadmap
    - Game title from metadata (instead of filename)
    - Search/sort buttons
    - Keymap support
    - Generate wheels/dmd somehow (?)
    - Music support (?)

### About

This is my personal frontend for my cabinet. It's As Simple As Possible. If you need help installing and configuring Visual Pinball X check my [wiki](https://github.com/surtarso/vpx-gui-tools/wiki/Visual-Pinball-X-on-Debian-Linux) page, also check my [vpx-gui-tools](https://github.com/surtarso/vpx-gui-tools/) to ease the process of settings tables up. I am also currently porting this project to C++/SDL [here](https://github.com/surtarso/ASAPCabinetFE/). (WIP)
