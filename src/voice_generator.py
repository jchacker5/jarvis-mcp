#!/usr/bin/env python3
import os
import sys
# torch is used indirectly by the generator module
import torch  # noqa: F401
import torchaudio
import argparse
import time
import threading


class TimeoutError(Exception):
    pass


def timeout(seconds):
    def decorator(function):
        def wrapper(*args, **kwargs):
            result = [
                TimeoutError(f"Function timed out after {seconds} seconds")
            ]
            
            def target():
                try:
                    result[0] = function(*args, **kwargs)
                except Exception as e:
                    result[0] = e
            
            t = threading.Thread(target=target)
            t.daemon = True
            t.start()
            t.join(seconds)
            
            if isinstance(result[0], Exception):
                raise result[0]
            return result[0]
        return wrapper
    return decorator


# Add the CSM directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
csm_dir = os.path.join(os.path.dirname(script_dir), "csm")
sys.path.append(csm_dir)

# Import CSM modules after adding to path
try:
    from csm.generator import load_csm_1b  # Try direct import first
except ImportError:
    # Fallback to regular import if direct import fails
    import generator  # noqa: E402


@timeout(60)  # 60 second timeout (increased from 30)
def load_model(ckpt_path, device):
    print("Loading model...")
    start_time = time.time()
    
    if 'load_csm_1b' in globals():
        gen = load_csm_1b(ckpt_path=ckpt_path, device=device)
    else:
        gen = generator.load_csm_1b(ckpt_path=ckpt_path, device=device)
    
    print(f"Model loaded in {time.time() - start_time:.2f} seconds")
    return gen


def generate_voice(text, output_path, speaker_id=0):
    """
    Generate audio from text using the CSM-1B model

    Args:
        text (str): The text to convert to speech
        output_path (str): Path to save the audio file
        speaker_id (int): Speaker ID to use (default: 0)
    """
    print(f"Generating audio for: {text}")

    # Check if MPS is available, otherwise use CPU
    if torch.backends.mps.is_available():
        device = "mps"
        print("MPS is available! Using MPS for faster generation.")
    else:
        device = "cpu"
        print("MPS not available. Using CPU.")
    
    print(f"Using device: {device}")

    # Load the model
    ckpt_path = os.path.join(csm_dir, "ckpt.pt")
    if not os.path.exists(ckpt_path):
        print(f"Error: Model checkpoint not found at {ckpt_path}")
        print("Please download the model checkpoint first.")
        sys.exit(1)

    # Use the appropriate load function based on which import succeeded
    try:
        gen = load_model(ckpt_path, device)
        
        # Generate audio
        print("Generating audio...")
        start_time = time.time()
        audio = gen.generate(
            text=text,
            speaker=speaker_id,
            context=[],
            temperature=0.7,
            topk=50
        )
        print(f"Audio generated in {time.time() - start_time:.2f} seconds")

        # Save the audio
        print("Saving audio...")
        torchaudio.save(output_path, audio.unsqueeze(0), gen.sample_rate)
        print(f"Audio saved to {output_path}")
    except TimeoutError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating audio: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate speech using CSM-1B model"
    )
    parser.add_argument(
        "--text", type=str, required=True, help="Text to convert to speech"
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Output audio file path"
    )
    parser.add_argument(
        "--speaker", type=int, default=0, help="Speaker ID (default: 0)"
    )
    parser.add_argument(
        "--force-cpu", 
        action="store_true", 
        help="Force CPU usage even if MPS is available"
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Override device selection if --force-cpu is specified
    if args.force_cpu:
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"
        print("Forcing CPU usage as requested")
    else:
        # Enable MPS fallback for operations not supported on MPS
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    generate_voice(args.text, args.output, args.speaker)
