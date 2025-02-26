# As Simple As Possible Cabinet Front-End

A front-end for your virtual pinball cabinet. As simple as possible.

## Features:
- Full screen display of table playfield and backglass
- Wheel and game title display
- Extended settings for many display configurations
- Extremely lightweight and simple
- No need to download artpacks, generate your own!*
- Just what it taked to make a cabinet look good

*Wheel generation not implemented yet.

## How to use:

X11: `python3 asap-cabinet-fe.py`

Wayland: `QT_QPA_PLATFORM=xcb python3 asap-cabinet-fe.py`

### Using the 'art generation' tool:

The script expects you to organize your tables by folders.

e.g. **tables/my_table/table_name.vpx**

It will scan your tables folder and open each table one by one, wait 12 seconds for the table to fully load and take a screenshot from both app screens (playfield and backglass).

It will than save those pictures in **tables/my_table/images/** as .png and they will be ready for the frontend to read. You still need to download the wheel images yourself.

Open the screenshot_art script and set your paths.

Double check and run: `./screenshot_art.sh` and wait.

## Roadmap
    - Video support
    - Music support
    - Game title from metadata (instead of filename)
    - Search/sort

### About

This is my personal frontend for my cabinet. It's as simple as possible. If you need help installing and configuring Visual Pinball X check my wiki page, also check my vpx-frontend tools to ease the process of settings tables up.
