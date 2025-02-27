# As Simple As Possible Cabinet Front-End

A dual screen front-end for your virtual pinball cabinet. "As Simple As Possible".

## Features:
- Full screen display of table playfield and backglass
- Wheel and game title display
- Extended settings for many display configurations
- Extremely lightweight and simple
- No need to download artpacks, generate your own!*
- Just what it takes to make a cabinet look good

*Playfield and Backglass from automated screenshots. Wheel and DMD generation not implemented yet.

## How to use:

- Dependencies: `sudo apt install python3 python3-pyqt5`

- X11: `python3 asap-cabinet-fe.py`

- Wayland: `QT_QPA_PLATFORM=xcb python3 asap-cabinet-fe.py`

### Using the 'art generation' tool:

The script expects you to organize your tables by folders.

e.g. **tables/my_table/table_name.vpx**

It will scan your tables folder and open each table one by one, wait 12 seconds for the table to fully load and take a screenshot from both app screens (playfield and backglass).

It will than save those pictures in **tables/my_table/images/** as .png and they will be ready for the frontend to display. You still need to download the wheel images yourself.

Dependencies: `sudo apt install xdotool imagemagick`

Edit the screenshot_art script and set your paths.

Dry-run to check results: `./screenshot_art.sh --dry-run`

Run the main script: `./screenshot_art.sh`

Flags: --wheel will display all tables without a wheel.png file.
       --dmd will display all tables without a dmd.gif file.
       --force will override existing table/backglass images with new ones.
       --dry-run will print execution without doing anything.

## Roadmap
    - Game title from metadata (instead of filename)
    - Search/sort buttons
    - Keymap support
    - Generate wheels/dmd somehow (?)
    - Music support (?)

### About

This is my personal frontend for my cabinet. It's As Simple As Possible. If you need help installing and configuring Visual Pinball X check my [wiki](https://github.com/surtarso/vpx-frontend/wiki) page, also check my [vpx-frontend](https://github.com/surtarso/vpx-frontend/) tools to ease the process of settings tables up.
