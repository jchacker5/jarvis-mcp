#!/bin/bash
# Test script for Jarvis MCP with MPS acceleration

echo "Testing Jarvis MCP with MPS acceleration"
echo "========================================"

# Activate virtual environment
source .venv/bin/activate

# Test voice generation with MPS
echo -e "\nTesting voice generation with MPS:"
PYTORCH_ENABLE_MPS_FALLBACK=1 python src/voice_generator.py \
  --text "Testing MPS acceleration for Jarvis voice generation." \
  --output test_mps.wav

# Play the generated audio
echo -e "\nPlaying generated audio:"
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  afplay test_mps.wav
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  aplay test_mps.wav
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  # Windows
  powershell -c "(New-Object Media.SoundPlayer 'test_mps.wav').PlaySync()"
else
  echo "Unsupported OS for audio playback"
fi

# Test the MCP directly
echo -e "\nTesting the MCP directly:"
node test-audio-mcp.js

echo -e "\nTest completed!" 