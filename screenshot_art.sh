#!/bin/bash
# Creates media (playfield + backglass) for asap-cabinet-fe
# Open all tables and screenshots playfield and backglass
# Saves them in table_name/images/ folder as:
# table.png and backglass.png
# This script is able to detect if those images already exist and skip. (--force to rebuild)
# You can check tables without wheels (images/wheel.png) using --missing flag.
# You can check tables without DMD animated gifs (images/dmd.gif) using --dmd flag.
# Use --dry-run to see the actions without changing anything.
#
# Dependencies: xdotool, imagemagick
# Tarso Galvão feb/2025

#set -x

# ANSI color codes
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE='\033[0;34m'
NC="\033[0m" # No Color

ROOT_FOLDER="/home/tarso/Games/vpinball/build/tables/"
VPX_EXECUTABLE="/home/tarso/Games/vpinball/build/VPinballX_GL"
SCREENSHOT_DELAY=12 #seconds
WINDOW_TITLE_VPX="Visual Pinball Player"
WINDOW_TITLE_BACKGLASS="B2SBackglass"

# Check for help flag
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo -e "${BLUE}Usage: $(basename "$0") [OPTIONS]${NC}"
    echo -e "${GREEN}Options:${NC}\n"
    echo -e "  ${BLUE}no argument     ${NC}Generate playfield and backglass images (default)"
    echo -e "  ${YELLOW}--dry-run       ${NC}Show what would be done without making changes"
    echo -e "  ${YELLOW}--missing       ${NC}List tables missing wheel.png image and exit"
    echo -e "  ${YELLOW}--force         ${NC}Recreate screenshots even if they already exist"
    echo -e "\n  ${YELLOW}-h, --help      ${NC}Show this help message and exit"
    exit 0
fi

DRY_RUN=false
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo -e "${YELLOW}Dry-run mode: No changes will be made.${NC}"
fi

# --missing argument, list tables missing wheel.png and exit.
if [ "$1" == "--missing" ]; then
    echo -e "${YELLOW}This script can't generate wheel images."
    echo -e "${BLUE}Using tables directory: $ROOT_FOLDER"
    echo -e "Checking for tables missing wheel.png...${NC}\n"
    # Iterate over each table directory that contains a .vpx file.
    for vpx_file in "$ROOT_FOLDER"/*/*.vpx; do
        if [ -f "$vpx_file" ]; then
            table_dir=$(dirname "$vpx_file")
            wheel_file="$table_dir/images/wheel.png"
            if [ ! -f "$wheel_file" ]; then
                echo -e "${GREEN}->${YELLOW} '$(basename "$table_dir")'${NC}"
            fi
        fi
    done
    echo -e "\n${BLUE}These tables have ${RED}no wheel.png${BLUE} images. You need to download them.${NC}"
    echo -e "${BLUE}Place them in ${YELLOW}$ROOT_FOLDER<table_folder>/images/${NC}"
    exit 0
fi

if [ "$1" == "--dmd" ]; then
    echo -e "${YELLOW}This script can't generate dmd videos."
    echo -e "${BLUE}Using tables directory: $ROOT_FOLDER"
    echo -e "Checking for tables missing dmd.gif...${NC}\n"
    # Iterate over each table directory that contains a .vpx file.
    for vpx_file in "$ROOT_FOLDER"/*/*.vpx; do
        if [ -f "$vpx_file" ]; then
            table_dir=$(dirname "$vpx_file")
            wheel_file="$table_dir/images/dmd.gif"
            if [ ! -f "$wheel_file" ]; then
                echo -e "${GREEN}->${YELLOW} '$(basename "$table_dir")'${NC}"
            fi
        fi
    done
    echo -e "\n${BLUE}These tables have ${RED}no dmd.gif${BLUE} images. You need to download them.${NC}"
    echo -e "${BLUE}Place them in ${YELLOW}$ROOT_FOLDER<table_folder>/images/${NC}"
    exit 0
fi

find "$ROOT_FOLDER" -name "*.vpx" | while read VPX_PATH; do
  TABLE_NAME=$(basename "$VPX_PATH" .vpx)
  IMAGES_FOLDER="$(dirname "$VPX_PATH")/images"
  TABLE_SCREENSHOT="$IMAGES_FOLDER/table.png"
  BACKGLASS_SCREENSHOT="$IMAGES_FOLDER/backglass.png"

  echo -e "${BLUE}Processing: $(basename "$(dirname "$VPX_PATH")")${NC}"

  # Check if images already exist
  if [ -f "$TABLE_SCREENSHOT" ] && [ -f "$BACKGLASS_SCREENSHOT" ]; then
    if [ "$1" == "--force" ]; then
      echo -e "${RED}Images found but ${YELLOW}--force${RED} used, overriding files.${NC}"
    else
      echo -e "${YELLOW}    Both images already exist for $(basename "$(dirname "$VPX_PATH")"), skipping.${NC}"
      continue # Skip to the next iteration
    fi
  fi

  if [ "$DRY_RUN" == true ]; then
    echo -e "${GREEN}    Would create screenshots for: $TABLE_NAME${NC}"
    continue
  fi

  mkdir -p "$IMAGES_FOLDER"

  # Launch VPinballX_GL (XWayland)
  WINE_X11_DRV=x11 "$VPX_EXECUTABLE" -play "$VPX_PATH" > /dev/null 2>&1 &
  VPX_PID=$!

  sleep "$SCREENSHOT_DELAY"

  # Capture VPinballX_GL screenshot (import) only if table screenshot doesn't exist
  if [ ! -f "$TABLE_SCREENSHOT" ]; then
    WINDOW_ID_VPX=$(xdotool search --name "$WINDOW_TITLE_VPX" | head -n 1)
    if [ -n "$WINDOW_ID_VPX" ]; then
      if ! import -window "$WINDOW_ID_VPX" "$TABLE_SCREENSHOT"; then
        echo -e "${RED}Error: import failed to capture table screenshot.${NC}"
      else
        echo -e "${GREEN}    Saved table screenshot: $TABLE_SCREENSHOT${NC}"
        # Strip incorrect sRGB profile to fix libpng warning
        mogrify -strip "$TABLE_SCREENSHOT"
      fi
    else
      echo -e "${RED}Error: VPinballX_GL window not found.${NC}"
    fi
  else
    echo -e "${YELLOW}    Table screenshot already exists, skipping capture.${NC}"
  fi

  # Capture backglass screenshot (import) only if backglass screenshot doesn't exist
  if [ ! -f "$BACKGLASS_SCREENSHOT" ]; then
    WINDOW_ID_BACKGLASS=$(xdotool search --name "$WINDOW_TITLE_BACKGLASS" | head -n 1)
    if [ -n "$WINDOW_ID_BACKGLASS" ]; then
      if ! import -window "$WINDOW_ID_BACKGLASS" "$BACKGLASS_SCREENSHOT"; then
        echo -e "${RED}Error: import failed to capture backglass screenshot.${NC}"
      else
        echo -e "${GREEN}    Saved backglass screenshot: $BACKGLASS_SCREENSHOT${NC}"
        # Strip incorrect sRGB profile to fix libpng warning
        mogrify -strip "$TABLE_SCREENSHOT"
      fi
    else
      echo -e "${RED}Error: B2SBackglass window not found.${NC}"
    fi
  else
    echo -e "${YELLOW}    Backglass screenshot already exists, skipping capture.${NC}"
  fi

  # kill VPX, gently
  kill "$VPX_PID"
  sleep 2
  if kill -0 "$VPX_PID" 2>/dev/null; then
      kill -9 "$VPX_PID"
  fi

  echo -e "${GREEN}Screenshots saved for $TABLE_NAME${NC}"
done

echo -e "${GREEN}Finished processing all tables.${NC}"
