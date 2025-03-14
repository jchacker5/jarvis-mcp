#!/usr/bin/env python3
"""
Script to download the CSM-1B model checkpoint from Hugging Face.
"""
import os
import sys
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    print("Error: huggingface_hub package not installed.")
    print("Please install it with: pip install huggingface_hub")
    sys.exit(1)


def download_model():
    """Download the CSM-1B model checkpoint."""
    print("Downloading CSM-1B model checkpoint...")

    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()

    # Create the csm directory if it doesn't exist
    csm_dir = script_dir / "csm"
    os.makedirs(csm_dir, exist_ok=True)

    # Download the model checkpoint
    try:
        file_path = hf_hub_download(
            repo_id="sesame/csm-1b",
            filename="ckpt.pt",
            local_dir=csm_dir
        )
        print(f"Model checkpoint downloaded successfully to: {file_path}")
        print("You can now build and run the Jarvis MCP.")
    except Exception as e:
        print(f"Error downloading model checkpoint: {e}")
        sys.exit(1)


if __name__ == "__main__":
    download_model()
