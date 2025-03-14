#!/usr/bin/env python3
"""
Comprehensive performance test for CSM-1B voice generation comparing CPU vs MPS.
This script tests both devices with multiple phrases and generates detailed reports.
"""
import os
import sys
import torch
import torchaudio
import argparse
import time
import json
from pathlib import Path

# Add the CSM directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
csm_dir = os.path.join(os.path.dirname(script_dir), "csm")
sys.path.append(csm_dir)

# Import CSM modules after adding to path
try:
    # First try importing directly from the csm directory
    sys.path.insert(0, csm_dir)
    from generator import load_csm_1b
except ImportError as e:
    print(f"Error importing generator module: {e}")
    print("Make sure the CSM model files are correctly installed")
    sys.exit(1)

# Test phrases to generate
TEST_PHRASES = [
    "Hello, I am Jarvis, your personal assistant.",
    "I have completed the task you requested, sir.",
    "Is there anything else you would like me to do for you today?",
    "The weather forecast predicts sunny skies with a high of 75 degrees.",
    "Your meeting with the development team is scheduled for 2 PM."
]

def test_device_performance(device_name, output_dir):
    """
    Test audio generation performance on a specific device
    
    Args:
        device_name (str): Device to test ('cpu' or 'mps')
        output_dir (str): Directory to save output files
    
    Returns:
        dict: Performance metrics
    """
    # Skip MPS if not available
    if device_name == 'mps' and not torch.backends.mps.is_available():
        print("MPS (Metal Performance Shaders) is not available on this system")
        return {
            "device": device_name,
            "available": False,
            "error": "MPS not available on this system"
        }
    
    results = {
        "device": device_name,
        "available": True,
        "model_load_time": 0,
        "generation_times": [],
        "total_generation_time": 0,
        "average_generation_time": 0
    }
    
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load model
        print(f"Loading model on {device_name}...")
        start_time = time.time()
        
        try:
            # Set environment variable for MPS fallback if using MPS
            if device_name == 'mps':
                os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
                print("Enabled MPS fallback for operations not supported on MPS")
            else:
                os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"
            
            # Load the model using the imported function
            gen = load_csm_1b(
                ckpt_path=os.path.join(csm_dir, "ckpt.pt"), 
                device=device_name
            )
            
            model_load_time = time.time() - start_time
            results["model_load_time"] = model_load_time
            print(f"Model loaded in {model_load_time:.2f} seconds")
            
            # Generate audio for each test phrase
            for i, phrase in enumerate(TEST_PHRASES):
                output_path = os.path.join(output_dir, f"{device_name}_test_{i}.wav")
                
                print(f"Generating audio for: '{phrase}'")
                start_time = time.time()
                
                audio = gen.generate(
                    text=phrase,
                    speaker=0,
                    context=[],
                    temperature=0.7,
                    topk=50
                )
                
                generation_time = time.time() - start_time
                results["generation_times"].append(generation_time)
                print(f"Audio generated in {generation_time:.2f} seconds")
                
                # Save the audio
                torchaudio.save(output_path, audio.unsqueeze(0), gen.sample_rate)
                print(f"Audio saved to {output_path}")
            
            # Calculate statistics
            results["total_generation_time"] = sum(results["generation_times"])
            results["average_generation_time"] = results["total_generation_time"] / len(TEST_PHRASES)
            
        except Exception as e:
            print(f"Error testing {device_name}: {e}")
            results["error"] = str(e)
            results["available"] = False
    
    except Exception as e:
        print(f"Error in test_device_performance for {device_name}: {e}")
        results["error"] = str(e)
        results["available"] = False
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Test CSM-1B performance on different devices"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="performance_test_results",
        help="Directory to save test results"
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep generated audio files (default: delete after test)"
    )
    parser.add_argument(
        "--cpu-only",
        action="store_true",
        help="Test only CPU performance, skip MPS"
    )
    parser.add_argument(
        "--mps-only",
        action="store_true",
        help="Test only MPS performance, skip CPU"
    )
    
    args = parser.parse_args()
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    # Determine which devices to test
    test_cpu = not args.mps_only
    test_mps = not args.cpu_only and torch.backends.mps.is_available()
    
    # Test CPU performance
    if test_cpu:
        print("\n=== Testing CPU Performance ===")
        cpu_results = test_device_performance("cpu", os.path.join(output_dir, "cpu"))
        results["cpu"] = cpu_results
        
        # Clean up audio files if not keeping them
        if not args.keep_audio and cpu_results["available"]:
            print("Cleaning up CPU audio files...")
            for i in range(len(TEST_PHRASES)):
                audio_path = os.path.join(output_dir, "cpu", f"cpu_test_{i}.wav")
                if os.path.exists(audio_path):
                    os.remove(audio_path)
    
    # Test MPS performance (Mac only)
    if test_mps:
        print("\n=== Testing MPS Performance ===")
        mps_results = test_device_performance("mps", os.path.join(output_dir, "mps"))
        results["mps"] = mps_results
        
        # Clean up audio files if not keeping them
        if not args.keep_audio and mps_results["available"]:
            print("Cleaning up MPS audio files...")
            for i in range(len(TEST_PHRASES)):
                audio_path = os.path.join(output_dir, "mps", f"mps_test_{i}.wav")
                if os.path.exists(audio_path):
                    os.remove(audio_path)
    elif not args.cpu_only:
        print("\nMPS (Metal Performance Shaders) is not available on this system")
        results["mps"] = {
            "device": "mps",
            "available": False,
            "error": "MPS not available on this system"
        }
    
    # Save results to JSON
    with open(os.path.join(output_dir, "performance_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate Markdown report
    generate_markdown_report(results, output_dir)
    
    print(f"\nTest completed. Results saved to {output_dir}")

def generate_markdown_report(results, output_dir):
    """Generate a Markdown report from the test results"""
    
    md_content = "# CSM-1B Voice Generation Performance Test\n\n"
    md_content += f"Test conducted on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # System information
    md_content += "## System Information\n\n"
    md_content += f"- Python version: {sys.version.split()[0]}\n"
    md_content += f"- PyTorch version: {torch.__version__}\n"
    md_content += f"- Operating system: {sys.platform}\n"
    md_content += f"- MPS available: {torch.backends.mps.is_available()}\n\n"
    
    # Results summary
    md_content += "## Results Summary\n\n"
    
    if (results.get("cpu", {}).get("available", False) and 
        results.get("mps", {}).get("available", False)):
        cpu_avg = results["cpu"]["average_generation_time"]
        mps_avg = results["mps"]["average_generation_time"]
        faster = "MPS" if mps_avg < cpu_avg else "CPU"
        speedup = max(cpu_avg, mps_avg) / min(cpu_avg, mps_avg)
        
        md_content += f"**{faster}** is faster by a factor of **{speedup:.2f}x**\n\n"
        
        # Add comparison table
        md_content += "| Metric | CPU | MPS | Difference |\n"
        md_content += "|--------|-----|-----|------------|\n"
        md_content += f"| Model Load Time | {results['cpu']['model_load_time']:.2f}s | {results['mps']['model_load_time']:.2f}s | {abs(results['cpu']['model_load_time'] - results['mps']['model_load_time']):.2f}s |\n"
        md_content += f"| Average Generation Time | {cpu_avg:.2f}s | {mps_avg:.2f}s | {abs(cpu_avg - mps_avg):.2f}s |\n"
        md_content += f"| Total Generation Time | {results['cpu']['total_generation_time']:.2f}s | {results['mps']['total_generation_time']:.2f}s | {abs(results['cpu']['total_generation_time'] - results['mps']['total_generation_time']):.2f}s |\n\n"
    
    # Detailed results
    md_content += "## Detailed Results\n\n"
    
    # CPU results
    if "cpu" in results:
        md_content += "### CPU Performance\n\n"
        if results["cpu"]["available"]:
            md_content += f"- Model load time: {results['cpu']['model_load_time']:.2f} seconds\n"
            md_content += f"- Total generation time: {results['cpu']['total_generation_time']:.2f} seconds\n"
            md_content += f"- Average generation time: {results['cpu']['average_generation_time']:.2f} seconds\n\n"
            
            md_content += "| Phrase | Generation Time (s) |\n"
            md_content += "|--------|--------------------|\n"
            for i, time_taken in enumerate(results["cpu"]["generation_times"]):
                if i < len(TEST_PHRASES):
                    phrase_display = TEST_PHRASES[i]
                    if len(phrase_display) > 40:
                        phrase_display = phrase_display[:37] + "..."
                    md_content += f"| {phrase_display} | {time_taken:.2f} |\n"
            md_content += "\n"
        else:
            md_content += f"Error: {results['cpu'].get('error', 'Unknown error')}\n\n"
    
    # MPS results
    if "mps" in results:
        md_content += "### MPS Performance\n\n"
        if results["mps"]["available"]:
            md_content += f"- Model load time: {results['mps']['model_load_time']:.2f} seconds\n"
            md_content += f"- Total generation time: {results['mps']['total_generation_time']:.2f} seconds\n"
            md_content += f"- Average generation time: {results['mps']['average_generation_time']:.2f} seconds\n\n"
            
            md_content += "| Phrase | Generation Time (s) |\n"
            md_content += "|--------|--------------------|\n"
            for i, time_taken in enumerate(results["mps"]["generation_times"]):
                if i < len(TEST_PHRASES):
                    phrase_display = TEST_PHRASES[i]
                    if len(phrase_display) > 40:
                        phrase_display = phrase_display[:37] + "..."
                    md_content += f"| {phrase_display} | {time_taken:.2f} |\n"
            md_content += "\n"
        else:
            md_content += f"Error: {results['mps'].get('error', 'Unknown error')}\n\n"
    
    # Conclusion
    md_content += "## Conclusion\n\n"
    
    if (results.get("cpu", {}).get("available", False) and 
        results.get("mps", {}).get("available", False)):
        cpu_avg = results["cpu"]["average_generation_time"]
        mps_avg = results["mps"]["average_generation_time"]
        
        if mps_avg < cpu_avg:
            md_content += f"MPS (Metal Performance Shaders) is **{(cpu_avg/mps_avg):.2f}x faster** than CPU for voice generation with CSM-1B. "
            md_content += "Consider using MPS for faster voice generation if available on your system.\n\n"
            md_content += "### Recommendations\n\n"
            md_content += "1. **Use MPS Acceleration**: Enable MPS acceleration in the Jarvis MCP by setting the `PYTORCH_ENABLE_MPS_FALLBACK=1` environment variable.\n"
            md_content += "2. **Implement Device Detection**: Automatically detect and use MPS when available, falling back to CPU when necessary.\n"
            md_content += "3. **Optimize Model Loading**: Consider implementing model caching to avoid reloading the model for each generation.\n"
        else:
            md_content += f"CPU is **{(mps_avg/cpu_avg):.2f}x faster** than MPS (Metal Performance Shaders) for voice generation with CSM-1B. "
            md_content += "Consider using CPU for voice generation with this model.\n\n"
            md_content += "### Recommendations\n\n"
            md_content += "1. **Use CPU Processing**: Disable MPS acceleration in the Jarvis MCP for better performance.\n"
            md_content += "2. **Investigate MPS Issues**: The unexpected performance difference might be due to model architecture or PyTorch implementation details.\n"
    elif results.get("cpu", {}).get("available", False):
        md_content += "Only CPU testing was successful. MPS testing failed or is not available on this system.\n\n"
    else:
        md_content += "Testing failed on both CPU and MPS.\n\n"
    
    # Write to file
    with open(os.path.join(output_dir, "performance_report.md"), "w") as f:
        f.write(md_content)

if __name__ == "__main__":
    main() 