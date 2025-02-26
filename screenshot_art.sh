#!/bin/bash
# Creates media (playfield + backglass) for asap-cabinet-fe
# Open all tables and screenshots playfield and backglass
# Saves them in table_name/images/ folder as:
# table.png and backglass.png
# This script is able to detect if those images already exist and skip.
# Dependencies: xdotool, imagemagick
# Tarso Galvão feb/2025

#set -x

# ANSI color codes
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

ROOT_FOLDER="/home/tarso/Games/vpinball/build/tables/"
VPX_EXECUTABLE="/home/tarso/Games/vpinball/build/VPinballX_GL"
SCREENSHOT_DELAY=12 #seconds
WINDOW_TITLE_VPX="Visual Pinball Player"
WINDOW_TITLE_BACKGLASS="B2SBackglass"

find "$ROOT_FOLDER" -name "*.vpx" | while read VPX_PATH; do
  TABLE_NAME=$(basename "$VPX_PATH" .vpx)
  IMAGES_FOLDER="$(dirname "$VPX_PATH")/images"
  TABLE_SCREENSHOT="$IMAGES_FOLDER/table.png"
  BACKGLASS_SCREENSHOT="$IMAGES_FOLDER/backglass.png"

  echo -e "${NC}Processing $VPX_PATH${NC}"

  # Check if images already exist
  if [ -f "$TABLE_SCREENSHOT" ] && [ -f "$BACKGLASS_SCREENSHOT" ]; then
    echo -e "${YELLOW}Images already exist for $TABLE_NAME, skipping.${NC}"
    continue # Skip to the next iteration
  fi

  mkdir -p "$IMAGES_FOLDER"

  # Launch VPinballX_GL (XWayland)
  WINE_X11_DRV=x11 "$VPX_EXECUTABLE" -play "$VPX_PATH" &
  VPX_PID=$!

  sleep "$SCREENSHOT_DELAY"

  # Capture VPinballX_GL screenshot (import)
  WINDOW_ID_VPX=$(xdotool search --name "$WINDOW_TITLE_VPX" | head -n 1)
  if [ -n "$WINDOW_ID_VPX" ]; then
    import -window "$WINDOW_ID_VPX" "$TABLE_SCREENSHOT"
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}Saved table screenshot: $TABLE_SCREENSHOT${NC}"
    else
      echo -e "${RED}Error: import failed to capture table screenshot.${NC}"
    fi
  else
    echo -e "${RED}Error: VPinballX_GL window not found.${NC}"
  fi

  # Capture backglass screenshot (import)
  WINDOW_ID_BACKGLASS=$(xdotool search --name "$WINDOW_TITLE_BACKGLASS" | head -n 1)
  if [ -n "$WINDOW_ID_BACKGLASS" ]; then
    import -window "$WINDOW_ID_BACKGLASS" "$BACKGLASS_SCREENSHOT"
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}Saved backglass screenshot: $BACKGLASS_SCREENSHOT${NC}"
    else
      echo -e "${RED}Error: import failed to capture backglass screenshot.${NC}"
    fi
  else
    echo -e "${RED}Error: B2SBackglass window not found.${NC}"
  fi

  kill -9 "$VPX_PID"
  if [ $? -ne 0 ]; then
    echo -e "${RED}Error: kill -9 failed for VPinballX_GL (PID: $VPX_PID)${NC}"
  fi
  wait "$VPX_PID"
  if [ $? -ne 0 ]; then
    echo -e "${RED}Error: wait failed for VPinballX_GL (PID: $VPX_PID)${NC}"
  fi

  echo -e "${GREEN}Screenshots saved for $TABLE_NAME${NC}"
done

echo -e "${GREEN}Finished processing all tables.${NC}"