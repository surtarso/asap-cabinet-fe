#!/bin/bash
# ------------------------------------------
# Create animated gif's from video files
# Useful for asap-cabinet-fe for DMD display
# Useful for Ultra.DMD tables in Linux
# ------------------------------------------
# Dependencies: ffmpeg, gifsicle
# Tarso Galvão feb/2025

# MP4
for i in *.mp4; do
    # Create GIF from MP4, maintaining the original resolution and aspect ratio
    ffmpeg -i "$i" -filter_complex "[0:v]fps=15,split=2[v1][v2];[v1]palettegen=stats_mode=diff:max_colors=256[pal];[v2][pal]paletteuse=dither=bayer:bayer_scale=3[out]" -map "[out]" "${i%.*}.gif"
done

# WMV
for i in *.wmv; do ffmpeg -i "$i" -filter_complex "[0:v]split=2[v1][v2];[v1]palettegen=stats_mode=diff:max_colors=256[pal];[v2][pal]paletteuse=dither=bayer:bayer_scale=3[out]" -map "[out]" "${i%.*}.gif"; done

# F4V
for i in *.f4v; do
    # Step 1: Generate a high-quality palette
    ffmpeg -i "$i" -vf "fps=15,palettegen=max_colors=256" -y "${i%.*}_palette.png"

    # Step 2: Use the generated palette to create a high-quality GIF
    ffmpeg -i "$i" -i "${i%.*}_palette.png" -filter_complex "[0:v]fps=15[pv];[pv][1:v]paletteuse=dither=sierra2_4a" -y "${i%.*}.gif"

    # Clean up temporary palette file
    rm "${i%.*}_palette.png"
done

# Optimize all animated gif's after conversion
gifsicle -O3 -k128 -V -j$(nproc) -b ./*.gif
