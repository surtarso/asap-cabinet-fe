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
- No need to download artpacks, [generate your own!*](https://github.com/surtarso/asap-cabinet-fe/tree/main/media_tools)
- Just what it takes to make a cabinet look good

*Playfield and Backglass from automated screenshots. Wheel and DMD generation not implemented yet.

## Installation:

- Download: `git clone https://github.com/surtarso/asap-cabinet-fe.git && cd asap-cabinet-fe/`

- Dependencies: `sudo apt install python3 python3-pyqt5 python3-pyqt5.qtmultimedia`

- X11: `./asap-cabinet-fe-x11` (or `python3 asap_cabinet_fe.py`)

- Wayland: `./asap-cabinet-fe` (or `QT_QPA_PLATFORM=xcb python3 asap_cabinet_fe.py`)

## Roadmap
    - Game title from metadata (instead of filename)
    - 'jump to letter' mechanics
    - Keymaping support
    - Generate wheels/dmd somehow (?)
    - Music support (?)

### About

This is my personal frontend for my cabinet. It's As Simple As Possible. If you need help installing and configuring Visual Pinball X check my [wiki](https://github.com/surtarso/vpx-gui-tools/wiki/Visual-Pinball-X-on-Debian-Linux) page, also check my [vpx-gui-tools](https://github.com/surtarso/vpx-gui-tools/) to ease the process of settings tables up. I am also currently porting this project to C++/SDL [here](https://github.com/surtarso/ASAPCabinetFE/). (WIP)
