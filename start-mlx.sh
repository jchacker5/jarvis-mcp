#!/bin/bash
# Start script for Jarvis MCP server with MLX-Audio
# This script starts the MCP server with integrated MLX-Audio support

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Activate the Python virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

# Check if MLX-Audio is installed
if ! pip list | grep -q "mlx-audio"; then
  echo "MLX-Audio is not installed. Please run setup.sh first."
  exit 1
fi

# Ensure the dist directory exists and TypeScript is compiled
if [ ! -d "dist" ] || [ ! -f "dist/index.js" ]; then
  echo "Building TypeScript files..."
  npm run build
fi

# Create audio directory if it doesn't exist
mkdir -p audio

# Launch the MCP server
echo "Starting Jarvis MCP server with MLX-Audio..."
node dist/index.js 