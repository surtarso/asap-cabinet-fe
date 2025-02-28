#!/bin/bash
# ------------------------------------------
# Create optimized animated GIFs from video files
# Useful for asap-cabinet-fe (DMD display) & UltraDMD in VPX Linux
# ------------------------------------------
# Dependencies: ffmpeg, gifsicle
# Usage:
#   -h, --help       Show help
#   --now            Run on the current folder
#   --path <dir>     Run on a specific directory
#   --optimize [dir] Only optimize existing GIFs (optionally in PATH)
#
# Tarso Galvão - Feb/2025

check_ffmpeg() {
    if ! command -v ffmpeg &> /dev/null; then
        echo "Error: ffmpeg is not installed. Please install it to proceed."
        echo "Debian: sudo apt install ffmpeg"
        exit 1
    fi
}

check_gifsicle() {
    if ! command -v gifsicle &> /dev/null; then
        echo "Error: gifsicle is not installed. Please install it to proceed."
        echo "Debian: sudo apt install gifsicle"
        exit 1
    fi
}

# Run checks
check_ffmpeg
check_gifsicle

show_help() {
    echo "Create optimized animated GIFs from video files"
    echo "Useful for asap-cabinet-fe (DMD display) & UltraDMD in VPX Linux"
    echo "Usage: $(basename "$0") [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  --now             Process videos in the current directory"
    echo "  --path <dir>      Process videos in a specified directory"
    echo "  --optimize <dir>  Only optimize existing GIFs (optionally in PATH)"
    echo ""
    exit 0
}

check_files_exist() {
    local folder="$1"
    local ext="$2"
    shopt -s nullglob
    files=("$folder"/*."$ext")
    shopt -u nullglob
    [[ ${#files[@]} -gt 0 ]]
}

optimize_gifs() {
    local folder="$1"
    if [[ ! -d "$folder" ]]; then
        echo "Error: Directory '$folder' not found."
        exit 1
    fi

    if ! check_files_exist "$folder" "gif"; then
        echo "No GIFs found to optimize. Exiting."
        exit 1
    else
        echo "Optimizing GIFs in: $folder"
        gifsicle -O3 -k128 -V -j"$(nproc)" -b "$folder"/*.gif
        echo "Done!"
    fi
}

process_video() {
    local folder="$1"
    local ext="$2"
    cd "$folder" || { echo "Error: Cannot access '$folder'"; exit 1; }

    if ! check_files_exist "$folder" "$ext"; then
        echo "No .$ext files found in $folder. Skipping..."
        return
    fi

    for i in *."$ext"; do
        [ -f "$i" ] || continue
        echo "Processing: $i"

        ffmpeg -i "$i" -vf "fps=15,palettegen=max_colors=256" -y "${i%.*}_palette.png"
        ffmpeg -i "$i" -i "${i%.*}_palette.png" -filter_complex "[0:v]fps=15[pv];[pv][1:v]paletteuse=dither=sierra2_4a" -y "${i%.*}.gif"
        rm "${i%.*}_palette.png"
    done
}

# Parse arguments
if [[ $# -eq 0 ]]; then
    show_help
fi

case "$1" in
    -h|--help)
        show_help
        ;;
    --now)
        folder="$(pwd)"
        ;;
    --path)
        if [[ -z "$2" || "$2" =~ ^- ]]; then
            echo "Error: --path requires a valid directory"
            exit 1
        fi
        folder="$2"
        ;;
    --optimize)
        if [[ -z "$2" || "$2" =~ ^- ]]; then
            folder="$(pwd)"
        else
            folder="$2"
        fi
        optimize_gifs "$folder"
        exit 0
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        ;;
esac

# Validate folder existence before proceeding
if [[ ! -d "$folder" ]]; then
    echo "Error: Directory '$folder' not found."
    exit 1
fi

# Check if any video files exist before processing
if ! check_files_exist "$folder" "mp4" && ! check_files_exist "$folder" "wmv" && ! check_files_exist "$folder" "f4v"; then
    echo "No supported video files (mp4, wmv, f4v) found in $folder. Exiting..."
    exit 1
fi

# Process MP4, WMV, and F4V files
for format in mp4 wmv f4v; do
    process_video "$folder" "$format"
done

# Optimize GIFs after conversion
optimize_gifs "$folder"

# Ask user if they want to delete original files
echo -n "Do you want to delete all original video files? Type 'yes' to confirm: "
read -r confirm

if [[ "$confirm" == "yes" ]]; then
    echo "Deleting original video files..."
    rm -v "$folder"/*.mp4 "$folder"/*.wmv "$folder"/*.f4v 2>/dev/null
    echo "Original files deleted."
else
    echo "Original files were kept."
fi
