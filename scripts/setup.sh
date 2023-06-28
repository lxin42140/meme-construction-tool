#!/bin/bash
# Description: Setting up of necessary directory folders for the ool
# Usage: on mac, use chmod +x setup.sh to give exec permission for this script before running it by ./setup.sh. Run this script before any other steps

set -e

# go to root dir
cd ..

# check if template is present
folder_path="templates"

if [ ! -d "$folder_path" ]; then
    echo "Error: templates/ dir does not exist." >&2
    exit 1
fi

echo "Creating necessary folders..."

# store processed template memes
mkdir -p processed_templates

mkdir -p output
cd output
# store created svg
mkdir -p svg
# store created image
mkdir -p image
# store ocr output
mkdir -p ocr
# store log files
mkdir -p logs

echo "Folders created successfully!"

# download weights
cd ../
cd model
file_path="ggml-alpaca-7b-q4.bin"
if [ -f "$file_path" ]; then
    echo "ggml-alpaca-7b-q4.bin already exists. Skipping download."
else
    echo "ggml-alpaca-7b-q4.bin does not exists and is necessary for chat tool. Starting download..."
    url="https://huggingface.co/Sosaka/Alpaca-native-4bit-ggml/resolve/main/ggml-alpaca-7b-q4.bin"
    output_file="ggml-alpaca-7b-q4.bin"
    curl -L -o "$output_file" "$url" # specify -L so that we can follow the redirect
fi