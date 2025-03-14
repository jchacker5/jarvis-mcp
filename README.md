# Jarvis MLX-Audio MCP

A high-quality voice generation system for Jarvis using MLX-Audio, optimized for Apple Silicon. This implementation uses the Model Context Protocol (MCP) to provide a standardized interface for AI assistants to generate speech.

## Features

- High-quality speech synthesis using MLX and the Kokoro TTS model
- Optimized for Apple Silicon (M1/M2/M3)
- Simple MCP server integration with one-command startup
- Multiple voice options
- Speed adjustment
- Minimal dependencies

## Prerequisites

- macOS with Apple Silicon (M1/M2/M3)
- Node.js v16 or higher
- Python 3.9 or higher

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/jarvis-mlx-audio-mcp.git
   cd jarvis-mlx-audio-mcp
   ```

2. Run the setup script:
   ```
   ./setup.sh
   ```

The setup script will:

- Install Node.js dependencies
- Create a Python virtual environment
- Install MLX-Audio and its dependencies
- Build the TypeScript code
- Create the necessary directories
- Make scripts executable

## Usage

### Starting the MCP Server

Start the MCP server with:

```
./start-mlx.sh
```

The server will run in the foreground and output logs to the console.

### Testing the Voice Generator

You can test the voice generator directly with:

```
./test-mlx-audio.sh --message "Hello, I am Jarvis, your AI assistant."
```

Options:

- `--message`: The text to convert to speech
- `--voice`: Voice style to use (default: af_heart)
- `--speed`: Speed multiplier (default: 1.0)
- `--output`: Output file path (default: test_mlx.wav)
- `--debug`: Enable debug mode with verbose logging

Available voices:

- `af_heart`: American female voice with a warm tone (default)
- `af_nova`: American female voice with a modern tone
- `af_bella`: American female voice with a soft tone
- `bf_emma`: British female voice

### Using with Claude

To use this MCP server with Claude:

1. Start the MCP server as described above
2. In your Cursor IDE, connect to the MCP server
3. Use the `speakJarvis` tool in Claude's custom instructions

Example custom instruction:

```
When a task is completed, use the speakJarvis tool with the task name to have Jarvis announce completion.
```

## Technical Details

This implementation uses:

- MLX-Audio for high-quality voice generation
- TypeScript for the MCP server
- Model Context Protocol (MCP) for standardized AI tool integration

## Troubleshooting

- If you encounter any issues with audio generation, try running the test script with `--debug` to get more detailed output
- Ensure you're running on Apple Silicon, as MLX is optimized for this architecture
- Make sure the virtual environment is activated before running any scripts

## License

MIT
