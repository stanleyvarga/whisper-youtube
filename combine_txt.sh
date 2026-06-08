#!/bin/bash

# Script to combine all txt files in the current directory into a master.txt file
# Usage: ./combine_txt.sh

# Get the directory where the script is run from
DIR="${1:-$(pwd)}"

# Output file
OUTPUT_FILE="$DIR/master.txt"

# Check if directory exists
if [ ! -d "$DIR" ]; then
    echo "Error: Directory '$DIR' does not exist"
    exit 1
fi

# Remove existing master.txt if it exists
if [ -f "$OUTPUT_FILE" ]; then
    echo "Removing existing master.txt..."
    rm "$OUTPUT_FILE"
fi

# Counter for article numbering
counter=1

# Find and process all txt files except master.txt, sorted alphabetically
for file in "$DIR"/*.txt; do
    # Skip master.txt itself
    if [ "$(basename "$file")" = "master.txt" ]; then
        continue
    fi
    
    # Check if file exists (in case no txt files found)
    if [ ! -f "$file" ]; then
        continue
    fi
    
    # Extract filename without extension as the title
    filename=$(basename "$file" .txt)
    
    echo "Processing: $(basename "$file")"
    
    # Add markdown header and file contents
    {
        echo "## $filename"
        echo ""
        cat "$file"
        echo ""
        echo ""
    } >> "$OUTPUT_FILE"
    
    ((counter++))
done

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: No txt files found in directory '$DIR'"
    exit 1
fi

echo "Successfully combined files into: $OUTPUT_FILE"
echo "Total files processed: $((counter - 1))"

