#!/bin/bash
# Test script for MLX-Audio voice generation
# This script directly tests the MLX-Audio voice generator

# Default values
MESSAGE="Hello, I am Jarvis, your AI assistant powered by MLX-Audio."
VOICE="af_heart"
SPEED=1.0
OUTPUT_FILE="test_mlx.wav"
DEBUG=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --message)
      MESSAGE="$2"
      shift 2
      ;;
    --voice)
      VOICE="$2"
      shift 2
      ;;
    --speed)
      SPEED="$2"
      shift 2
      ;;
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    --debug)
      DEBUG="--debug"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--message \"text\"] [--voice voice_style] [--speed speed_value] [--output output_file] [--debug]"
      exit 1
      ;;
  esac
done

# Ensure the audio directory exists
mkdir -p audio

# Activate the virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

# Run the voice generator directly
echo "Generating audio for: \"$MESSAGE\""
echo "Using voice: $VOICE, speed: $SPEED"
echo "Output file: $OUTPUT_FILE"
if [[ -n "$DEBUG" ]]; then
  echo "Debug mode: enabled"
fi

python src/mlx_voice_generator.py --text "$MESSAGE" --voice "$VOICE" --speed "$SPEED" --output "$OUTPUT_FILE" $DEBUG

# Check if the audio file was created
if [ -f "$OUTPUT_FILE" ]; then
  echo "Audio generated successfully: $OUTPUT_FILE"
  
  # Play the audio file
  if [[ "$OSTYPE" == "darwin"* ]]; then
    afplay "$OUTPUT_FILE"
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    aplay "$OUTPUT_FILE"
  elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    powershell -c "(New-Object Media.SoundPlayer \"$OUTPUT_FILE\").PlaySync()"
  else
    echo "Cannot play audio on this platform. Please play the file manually: $OUTPUT_FILE"
  fi
  
  echo "Test completed successfully!"
else
  echo "Failed to generate audio file: $OUTPUT_FILE"
  exit 1
fi 