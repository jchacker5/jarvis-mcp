#!/usr/bin/env python3
"""
Simple performance test for CSM-1B voice generation comparing CPU vs MPS.
"""
import os
import sys
import time
import torch
import argparse

# Test phrases
TEST_PHRASES = [
    "Hello, I am Jarvis, your personal assistant.",
    "I have completed the task you requested, sir."
]

# Results storage
results = {
    "cpu": {"available": True, "times": []},
    "mps": {"available": False, "times": []}
}

def main():
    parser = argparse.ArgumentParser(description="Test CSM-1B performance")
    parser.add_argument("--output", type=str, default="performance_results.md",
                        help="Output markdown file")
    args = parser.parse_args()
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Check if MPS is available
    if torch.backends.mps.is_available():
        results["mps"]["available"] = True
        print("MPS (Metal Performance Shaders) is available")
    else:
        print("MPS is not available on this system")
    
    # Run the voice generator script for each device and phrase
    for device in ["cpu", "mps"]:
        if not results[device]["available"]:
            continue
        
        print(f"\n=== Testing {device.upper()} Performance ===")
        
        for phrase in TEST_PHRASES:
            output_file = f"test_{device}_{int(time.time())}.wav"
            
            # Time the voice generation
            start_time = time.time()
            
            # Run the voice generator script
            cmd = f"python src/voice_generator.py --text \"{phrase}\" --output {output_file}"
            if device == "mps":
                # Add environment variable to use MPS
                cmd = f"PYTORCH_ENABLE_MPS_FALLBACK=1 {cmd}"
            else:
                # Force CPU usage
                cmd = f"{cmd} --force-cpu"
            
            print(f"Running: {cmd}")
            exit_code = os.system(cmd)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if exit_code == 0:
                print(f"Generated audio in {duration:.2f} seconds")
                results[device]["times"].append(duration)
                
                # Clean up the output file
                if os.path.exists(output_file):
                    os.remove(output_file)
            else:
                print(f"Failed to generate audio on {device}")
    
    # Calculate averages
    for device in ["cpu", "mps"]:
        if results[device]["available"] and results[device]["times"]:
            results[device]["average"] = sum(results[device]["times"]) / len(results[device]["times"])
        else:
            results[device]["available"] = False
    
    # Generate report
    generate_report(args.output)
    
    print(f"\nResults saved to {args.output}")

def generate_report(output_file):
    """Generate a markdown report of the results"""
    
    md = "# CSM-1B Voice Generation Performance Test\n\n"
    md += f"Test conducted on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # System information
    md += "## System Information\n\n"
    md += f"- Python version: {sys.version.split()[0]}\n"
    md += f"- PyTorch version: {torch.__version__}\n"
    md += f"- Operating system: {sys.platform}\n"
    md += f"- MPS available: {torch.backends.mps.is_available()}\n\n"
    
    # Results
    md += "## Results\n\n"
    
    # CPU results
    md += "### CPU Performance\n\n"
    if results["cpu"]["available"] and "average" in results["cpu"]:
        md += f"- Average generation time: {results['cpu']['average']:.2f} seconds\n\n"
        
        md += "| Phrase | Generation Time (s) |\n"
        md += "|--------|--------------------|\n"
        for i, time_taken in enumerate(results["cpu"]["times"]):
            if i < len(TEST_PHRASES):
                md += f"| {TEST_PHRASES[i]} | {time_taken:.2f} |\n"
        md += "\n"
    else:
        md += "CPU testing failed or was not performed.\n\n"
    
    # MPS results
    md += "### MPS Performance\n\n"
    if results["mps"]["available"] and "average" in results["mps"]:
        md += f"- Average generation time: {results['mps']['average']:.2f} seconds\n\n"
        
        md += "| Phrase | Generation Time (s) |\n"
        md += "|--------|--------------------|\n"
        for i, time_taken in enumerate(results["mps"]["times"]):
            if i < len(TEST_PHRASES):
                md += f"| {TEST_PHRASES[i]} | {time_taken:.2f} |\n"
        md += "\n"
    else:
        md += "MPS testing failed or was not performed.\n\n"
    
    # Comparison
    md += "## Comparison\n\n"
    
    if (results["cpu"]["available"] and "average" in results["cpu"] and
        results["mps"]["available"] and "average" in results["mps"]):
        
        cpu_avg = results["cpu"]["average"]
        mps_avg = results["mps"]["average"]
        
        if cpu_avg < mps_avg:
            faster = "CPU"
            speedup = mps_avg / cpu_avg
        else:
            faster = "MPS"
            speedup = cpu_avg / mps_avg
        
        md += f"**{faster}** is faster by a factor of **{speedup:.2f}x**\n\n"
        
        if faster == "MPS":
            md += "Consider using MPS for faster voice generation if available on your system.\n"
        else:
            md += "CPU is faster for this model, which is unexpected. This might be due to the overhead of transferring data to the GPU or other factors.\n"
    else:
        md += "Comparison not possible as testing failed on one or both devices.\n"
    
    # Write to file
    with open(output_file, "w") as f:
        f.write(md)

if __name__ == "__main__":
    main() 