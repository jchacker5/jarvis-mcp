#!/bin/bash
# Setup script for Jarvis MCP

set -e  # Exit on error

echo "Setting up Jarvis MCP..."

# Check if Python 3.10 is installed
if ! command -v python3.10 &> /dev/null; then
    echo "Error: Python 3.10 is required but not found."
    echo "Please install Python 3.10 and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not found."
    echo "Please install Node.js and try again."
    exit 1
fi

# Create Python virtual environment
echo "Creating Python virtual environment..."
python3.10 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r csm/requirements.txt
pip install huggingface_hub

# Download the model checkpoint
echo "Downloading CSM-1B model checkpoint..."
python download_model.py

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Build the TypeScript code
echo "Building TypeScript code..."
npm run build

echo "Setup complete! You can now run the Jarvis MCP with: npm start"
echo ""
echo "To use in Cursor:"
echo "1. Open Cursor settings"
echo "2. Navigate to the MCPs section"
echo "3. Add a new MCP with the command: node $(pwd)/dist/index.js"
echo ""
echo "Add to your Cursor prompt rules:"
echo "When a task is completed, use the speakJarvis tool with the task name to have Jarvis announce completion." 