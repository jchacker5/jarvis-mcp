#!/bin/bash
# Setup script for Jarvis MLX-Audio MCP
# This script installs all dependencies needed for the project

echo "Setting up Jarvis MLX-Audio MCP..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js v16 or higher."
    exit 1
fi

# Check Node.js version
node_version=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$node_version" -lt 16 ]; then
    echo "Node.js v16+ is required. You have $(node -v)."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1-2)
min_version="3.9"
if [ "$(printf '%s\n' "$min_version" "$python_version" | sort -V | head -n1)" != "$min_version" ]; then
    echo "Python 3.9+ is required. You have Python $python_version."
    exit 1
fi

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Create a Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv .venv

# Activate the virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install Python dependencies
echo "Installing MLX-Audio and dependencies..."
pip install --upgrade pip
pip install mlx-audio

# Build TypeScript code
echo "Building TypeScript code..."
npm run build

# Create audio directory if it doesn't exist
mkdir -p audio

# Make scripts executable
echo "Making scripts executable..."
chmod +x start-mlx.sh
chmod +x test-mlx-audio.sh

echo "Setup complete! You can now run the MCP server:"
echo "  ./start-mlx.sh"
echo ""
echo "To test the audio generation:"
echo "  ./test-mlx-audio.sh --message \"Hello, I am Jarvis.\""

echo "Thank you for using Jarvis MLX-Audio MCP!" 