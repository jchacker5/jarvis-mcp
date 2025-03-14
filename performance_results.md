# CSM-1B Voice Generation Performance Test

Test conducted on: 2025-03-13 19:44:57

## System Information

- Python version: 3.11.5
- PyTorch version: 2.4.0
- Operating system: darwin
- MPS available: True

## Results

### CPU Performance

- Average generation time: 90.74 seconds

| Phrase | Generation Time (s) |
|--------|--------------------|
| Hello, I am Jarvis, your personal assistant. | 145.27 |
| I have completed the task you requested, sir. | 36.22 |

### MPS Performance

- Average generation time: 43.96 seconds

| Phrase | Generation Time (s) |
|--------|--------------------|
| Hello, I am Jarvis, your personal assistant. | 47.14 |
| I have completed the task you requested, sir. | 40.78 |

## Comparison

**MPS** is faster by a factor of **2.06x**

Consider using MPS for faster voice generation if available on your system.
