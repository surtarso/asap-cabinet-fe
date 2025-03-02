#!/bin/bash
# -----------------------------------------------------------------------------
# This script processes VPX table files in the specified ROOT_FOLDER.
# It captures animated GIFs (5 seconds long; 10 frames at 0.5 sec intervals)
# from:
#   - The table window ("Visual Pinball Player")
#   - The backglass window ("B2SBackglass")
#
# Modes:
#   --now                : Process both windows (default behavior if --now is used)
#                          (Will only build missing GIFs unless --force is used)
#   --tables-only, -t    : Capture only the table window animated GIF.
#                          Optionally provide a specific table path (directory or VPX file).
#   --backglass-only, -b : Capture only the backglass window animated GIF.
#                          Optionally provide a specific table path (directory or VPX file).
#   --force              : Force rebuilding GIFs even if they already exist.
#
# Running without any flag or with -h/--help displays this usage message.
#
# Dependencies: xdotool, ImageMagick (import, convert)
#
# Author: Tarso Galvão, Feb/2025 (Modified to use process groups and wait for capture jobs)
# -----------------------------------------------------------------------------




# TODO: add a flag to switch between gifs and mp4s generation!



# ANSI color codes for output
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m"  # No Color

# ---------------------------------------------------------------------------
# Configuration variables
# ---------------------------------------------------------------------------
ROOT_FOLDER="/home/tarso/Games/vpinball/build/tables/"
VPX_EXECUTABLE="/home/tarso/Games/vpinball/build/VPinballX_GL"
SCREENSHOT_DELAY=12  # Seconds to wait after launching VPX
# Animated GIF settings: 
# For ~5 seconds: 10 frames, one every 0.5 seconds
# For ~3 seconds: 6 frames, one every 0.5 seconds 
FRAME_COUNT=6
FRAME_INTERVAL=0.5  # Seconds between frames
CONVERT_DELAY=50    # Delay for each frame in the GIF (50/100 sec per frame)

# Window titles to capture
WINDOW_TITLE_VPX="Visual Pinball Player"
WINDOW_TITLE_BACKGLASS="B2SBackglass"

# ---------------------------------------------------------------------------
# Usage function
# ---------------------------------------------------------------------------
usage() {
    echo "Processes VPX tables in the specified ROOT_FOLDER."
    echo "It captures animated GIFs (5 seconds long) from the table and backglass window"
    echo "and saves them in /images/table.gif and /images/backglass.gif"
    echo -e "${BLUE}Usage:${NC} $0 [--now | --tables-only|-t [<table_path>] | --backglass-only|-b [<table_path>]] [--force]"
    echo ""
    echo "  --now                Run full mode (capture both table and backglass),"
    echo "                       but only create GIFs for missing images unless --force is used."
    echo "  --tables-only, -t    Capture only the table window animated GIF."
    echo "                       Optionally provide a specific table path (directory or VPX file)."
    echo "  --backglass-only, -b Capture only the backglass window animated GIF."
    echo "                       Optionally provide a specific table path (directory or VPX file)."
    echo "  --force              Force rebuilding GIFs even if they already exist."
    echo "  -h, --help           Display this help message and exit."
    echo "  --clean              Removes all animated gif (created by this script)"
    exit 1
}

# ---------------------------------------------------------------------------
# Parse command-line arguments
# ---------------------------------------------------------------------------
MODE=""
SPECIFIC_PATH=""
FORCE="false"

if [ "$#" -eq 0 ]; then
    usage
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        --help|-h)
            usage
            ;;
        --now)
            MODE="now"
            shift
            ;;
        --tables-only|-t)
            MODE="tables-only"
            shift
            if [ "$#" -gt 0 ] && [[ "$1" != -* ]]; then
                SPECIFIC_PATH="$1"
                shift
            fi
            ;;
        --backglass-only|-b)
            MODE="backglass-only"
            shift
            if [ "$#" -gt 0 ] && [[ "$1" != -* ]]; then
                SPECIFIC_PATH="$1"
                shift
            fi
            ;;
        --force)
            FORCE="true"
            shift
            ;;
        --clean)
            MODE="clean"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# If no valid mode is set, display help
if [ -z "$MODE" ]; then
    usage
fi

if [ "$MODE" == "clean" ]; then
    echo -e "${YELLOW}Cleaning all table.gif and backglass.gif images from all tables...${NC}"
    find "$ROOT_FOLDER" -type f \( -name "table.gif" -o -name "backglass.gif" \) -exec rm -v {} \;
    exit 0
fi

# ---------------------------------------------------------------------------
# Dependency checks: Ensure required commands are available.
# ---------------------------------------------------------------------------
command -v xdotool >/dev/null 2>&1 || {
    echo -e "${RED}Error: xdotool is not installed. Please install it (e.g., sudo apt install xdotool).${NC}";
    exit 1;
}

command -v import >/dev/null 2>&1 || {
    echo -e "${RED}Error: ImageMagick (import) is not installed. Please install it (e.g., sudo apt install imagemagick).${NC}";
    exit 1;
}

command -v convert >/dev/null 2>&1 || {
    echo -e "${RED}Error: ImageMagick (convert) is not installed. Please install it (e.g., sudo apt install imagemagick).${NC}";
    exit 1;
}

# ---------------------------------------------------------------------------
# Build list of VPX files to process.
# If a specific table path is provided, use it; otherwise process all tables.
# ---------------------------------------------------------------------------
VPX_LIST=""
if [ -n "$SPECIFIC_PATH" ]; then
    if [ -d "$SPECIFIC_PATH" ]; then
        VPX_FILE=$(find "$SPECIFIC_PATH" -maxdepth 1 -type f -name "*.vpx" | head -n 1)
        if [ -z "$VPX_FILE" ]; then
            echo -e "${RED}Error: No .vpx file found in directory $SPECIFIC_PATH${NC}"
            exit 1
        fi
        VPX_LIST="$VPX_FILE"
    elif [ -f "$SPECIFIC_PATH" ]; then
        VPX_LIST="$SPECIFIC_PATH"
    else
        echo -e "${RED}Error: Specified path '$SPECIFIC_PATH' is not valid.${NC}"
        exit 1
    fi
else
    VPX_LIST=$(find "$ROOT_FOLDER" -name "*.vpx")
fi

# ---------------------------------------------------------------------------
# Process each VPX file (each table)
# ---------------------------------------------------------------------------
echo -e "${GREEN}Processing VPX files...${NC}"
echo "$VPX_LIST" | while read VPX_PATH; do
    # Derive table name and images folder
    TABLE_NAME=$(basename "$VPX_PATH" .vpx)
    TABLE_DIR=$(dirname "$VPX_PATH")
    VIDEO_FOLDER="${TABLE_DIR}/video"
    TABLE_GIF="$VIDEO_FOLDER/table.gif"
    BACKGLASS_GIF="$VIDEO_FOLDER/backglass.gif"

    echo -e "${BLUE}Processing: $(basename "$TABLE_DIR")${NC}"
    mkdir -p "$VIDEO_FOLDER"

    # ----------------------------------------------------------------------
    # Check if GIFs already exist and skip processing entirely if so
    # ----------------------------------------------------------------------
    if [[ "$MODE" == "now" && -f "$TABLE_GIF" && -f "$BACKGLASS_GIF" && "$FORCE" != "true" ]]; then
        echo -e "${YELLOW}Both animated GIFs already exist for $(basename "$TABLE_DIR"), skipping.${NC}"
        continue
    fi
    if [[ "$MODE" == "tables-only" && -f "$TABLE_GIF" && "$FORCE" != "true" ]]; then
        echo -e "${YELLOW}Table animated GIF already exists for $(basename "$TABLE_DIR"), skipping.${NC}"
        continue
    fi
    if [[ "$MODE" == "backglass-only" && -f "$BACKGLASS_GIF" && "$FORCE" != "true" ]]; then
        echo -e "${YELLOW}Backglass animated GIF already exists for $(basename "$TABLE_DIR"), skipping.${NC}"
        continue
    fi

    # ----------------------------------------------------------------------
    # Launch VPX in its own process group so that all child processes can be killed
    # ----------------------------------------------------------------------
    echo -e "${YELLOW}Launching VPX for $(basename "$TABLE_DIR")${NC}"
    setsid "$VPX_EXECUTABLE" -play "$VPX_PATH" > /dev/null 2>&1 &
    VPX_PID=$!

    # Wait for the VPX windows to load
    sleep "$SCREENSHOT_DELAY"

    # Array to collect background capture process IDs
    capture_pids=()

    # ----------------------------------------------------------------------
    # Capture table animated GIF if mode is now or tables-only
    # ----------------------------------------------------------------------
    if [[ "$MODE" == "now" || "$MODE" == "tables-only" ]]; then
        WINDOW_ID_VPX=$(xdotool search --name "$WINDOW_TITLE_VPX" | head -n 1)
        if [ -n "$WINDOW_ID_VPX" ]; then
            TMP_TABLE_DIR=$(mktemp -d "$VIDEO_FOLDER/table_tmp_XXXXXX")
            (
                for i in $(seq 0 $((FRAME_COUNT - 1))); do
                    FRAME_FILE="${TMP_TABLE_DIR}/frame_${i}.png"
                    import -window "$WINDOW_ID_VPX" "$FRAME_FILE"
                    sleep "$FRAME_INTERVAL"
                done
                convert -delay "$CONVERT_DELAY" -loop 0 "${TMP_TABLE_DIR}"/frame_*.png "$TABLE_GIF"
                rm -rf "$TMP_TABLE_DIR"
                echo -e "${GREEN}Saved table animated GIF: $TABLE_GIF${NC}"
            ) &
            capture_pids+=($!)
        else
            echo -e "${RED}Error: VPinballX_GL window not found.${NC}"
        fi
    fi

    # ----------------------------------------------------------------------
    # Capture backglass animated GIF if mode is now or backglass-only
    # ----------------------------------------------------------------------
    if [[ "$MODE" == "now" || "$MODE" == "backglass-only" ]]; then
        WINDOW_ID_BACKGLASS=$(xdotool search --name "$WINDOW_TITLE_BACKGLASS" | head -n 1)
        if [ -n "$WINDOW_ID_BACKGLASS" ]; then
            TMP_BACKGLASS_DIR=$(mktemp -d "$VIDEO_FOLDER/backglass_tmp_XXXXXX")
            (
                for i in $(seq 0 $((FRAME_COUNT - 1))); do
                    FRAME_FILE="${TMP_BACKGLASS_DIR}/frame_${i}.png"
                    import -window "$WINDOW_ID_BACKGLASS" "$FRAME_FILE"
                    sleep "$FRAME_INTERVAL"
                done
                convert -delay "$CONVERT_DELAY" -loop 0 "${TMP_BACKGLASS_DIR}"/frame_*.png "$BACKGLASS_GIF"
                rm -rf "$TMP_BACKGLASS_DIR"
                echo -e "${GREEN}Saved backglass animated GIF: $BACKGLASS_GIF${NC}"
            ) &
            capture_pids+=($!)
        else
            echo -e "${RED}Error: B2SBackglass window not found.${NC}"
        fi
    fi

    # Wait for the capture jobs to finish (do not wait for VPX)
    for pid in "${capture_pids[@]}"; do
        wait "$pid"
    done

    # ----------------------------------------------------------------------
    # Terminate the entire VPX process group
    # ----------------------------------------------------------------------
    echo -e "${YELLOW}Terminating VPX process group (PGID: $VPX_PID)${NC}"
    kill -TERM -- -"$VPX_PID" 2>/dev/null
    sleep 2
    if kill -0 -- -"$VPX_PID" 2>/dev/null; then
        kill -9 -- -"$VPX_PID" 2>/dev/null
    fi

    echo -e "${GREEN}Finished processing table: $TABLE_NAME${NC}"
done

echo -e "${GREEN}Finished processing all VPX files.${NC}"
