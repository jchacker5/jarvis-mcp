#!/usr/bin/env python3
"""
MLX Voice Generator

A high-quality voice generator using MLX-Audio optimized for Apple Silicon.
This script generates audio files from text using various voice styles.

Available voices:
- af_heart: American female voice with a warm tone (default)
- af_nova: American female voice with a modern tone
- af_bella: American female voice with a soft tone
- bf_emma: British female voice

Speed can range from 0.5 (slower) to 2.0 (faster).
"""

import os
import sys
import argparse
import traceback
import soundfile as sf
import mlx.core as mx

# Set default values
DEFAULT_VOICE = "af_heart"
DEFAULT_OUTPUT = "output.wav"
DEFAULT_SPEED = 1.0
DEBUG = False


def generate_audio(
    text, voice=DEFAULT_VOICE, speed=DEFAULT_SPEED, output_path=DEFAULT_OUTPUT
):
    """
    Generate audio from text using MLX-Audio.
    
    Args:
        text (str): Text to convert to speech
        voice (str): Voice model to use
        speed (float): Speed adjustment factor (1.0 is normal speed)
        output_path (str): Path to save the generated audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if DEBUG:
        print("Generate audio called with:")
        print(f"  Text: {text}")
        print(f"  Voice: {voice}")
        print(f"  Speed: {speed}")
        print(f"  Output path: {output_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(
        os.path.dirname(os.path.abspath(output_path)) or ".", 
        exist_ok=True
    )
    
    try:
        # Import here to avoid loading models unless needed
        from mlx_audio.tts.utils import load_model
        
        if DEBUG:
            print("Initializing MLX-Audio model...")
        
        # Load the model
        model = load_model("prince-canuma/Kokoro-82M")
        
        if DEBUG:
            print("Model loaded successfully")
            print(f"Generating audio for text: {text}")
        
        # Generate audio
        results = model.generate(
            text=text,
            voice=voice,
            speed=speed,
            lang_code="a",  # American English
            verbose=DEBUG
        )
        
        # Get the audio data
        audio_list = []
        for result in results:
            audio_list.append(result.audio)
        
        # Combine audio segments if there are multiple
        if len(audio_list) > 1:
            if DEBUG:
                print(f"Combining {len(audio_list)} audio segments")
            audio = mx.concatenate(audio_list, axis=0)
        else:
            audio = audio_list[0]
        
        # Save the audio
        if DEBUG:
            print(f"Saving audio to {output_path}")
        
        sf.write(output_path, audio, 24000)
        
        if DEBUG:
            print("Audio saved successfully")
        
        return True
    except ImportError as e:
        print(f"Error importing MLX-Audio: {e}")
        print("Please install MLX-Audio with: pip install mlx-audio")
        if DEBUG:
            traceback.print_exc()
        return False
    except Exception as e:
        print(f"Error generating audio: {e}")
        if DEBUG:
            traceback.print_exc()
        return False


def main():
    """Parse command-line arguments and generate audio."""
    parser = argparse.ArgumentParser(description="MLX Voice Generator")
    parser.add_argument(
        "--text", 
        type=str, 
        required=True, 
        help="Text to convert to speech"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default=DEFAULT_OUTPUT, 
        help="Output audio file path"
    )
    parser.add_argument(
        "--voice", 
        type=str, 
        default=DEFAULT_VOICE, 
        help="Voice style to use"
    )
    parser.add_argument(
        "--speed", 
        type=float, 
        default=DEFAULT_SPEED, 
        help="Speech speed multiplier"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set debug flag
    global DEBUG
    if args.debug:
        DEBUG = True
        print("Debug mode enabled")
    
    success = generate_audio(args.text, args.voice, args.speed, args.output)
    
    if success:
        print(f"Audio generated successfully: {args.output}")
        sys.exit(0)
    else:
        print("Failed to generate audio")
        sys.exit(1)


if __name__ == "__main__":
    main() 