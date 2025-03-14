# Jarvis MCP for Cursor

A Model Context Protocol (MCP) for Cursor that speaks with a Jarvis-like voice after task completion.

## Features

- Integrates with Cursor IDE through the MCP protocol
- Uses the CSM-1B voice model from Sesame AI Labs to generate Jarvis-like voice responses
- Speaks aloud when tasks are completed with the phrase: "I have completed [task] sir, is there anything else you'd like me to do."
- Utilizes MPS (Metal Performance Shaders) acceleration on Apple Silicon Macs for up to 2x faster voice generation

## Prerequisites

- Node.js (v18 or later)
- Python 3.10 or later
- Cursor IDE
- For optimal performance on Mac: Apple Silicon hardware (M1/M2/M3)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/jarvis-mcp.git
   cd jarvis-mcp
   ```

2. Install Node.js dependencies:

   ```bash
   npm install
   ```

3. Set up the Python environment for the CSM voice model:

   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r csm/requirements.txt
   ```

4. Download the CSM-1B model checkpoint:

   ```bash
   pip install huggingface_hub
   python -c "from huggingface_hub import hf_hub_download; hf_hub_download('sesame/csm-1b', 'ckpt.pt', local_dir='csm')"
   ```

5. Build the TypeScript code:
   ```bash
   npm run build
   ```

## Usage

1. Start the Jarvis MCP server:

   ```bash
   npm start
   ```

2. In Cursor, add the MCP to your configuration:

   - Open Cursor settings
   - Navigate to the MCPs section
   - Add a new MCP with the command: `node /path/to/jarvis-mcp/dist/index.js`

3. Add the following to your Cursor prompt rules:
   ```
   When a task is completed, use the speakJarvis tool with the task name to have Jarvis announce completion.
   ```

## API

The Jarvis MCP provides the following tool:

### `speakJarvis`

Generates and plays a Jarvis-like voice response.

Parameters:

- `task` (optional): The name of the completed task
- `customMessage` (optional): A custom message to speak instead of the default

Example:

```javascript
// In Cursor's AI response
speakJarvis({ task: "creating the React component" });
```

## Troubleshooting

- **Audio not playing**: Make sure your system's audio is working and not muted
- **Python errors**: Verify that you have the correct Python version (3.10) and all dependencies installed
- **Model not found**: Ensure you've downloaded the model checkpoint to the correct location

## License

ISC

## Acknowledgements

- [Sesame AI Labs](https://huggingface.co/sesame) for the CSM-1B voice model
- [Model Context Protocol](https://github.com/cursor-io/model-context-protocol) for the MCP specification

## Performance

On Apple Silicon Macs, the Jarvis MCP automatically uses MPS (Metal Performance Shaders) acceleration for voice generation, which provides approximately 2x faster performance compared to CPU-only generation. This results in more responsive voice feedback after task completion.

### Performance Testing

To run performance tests comparing CPU and MPS:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the simple performance test
python simple-performance-test.py

# Run the comprehensive performance test
./test-performance.py

# Test MPS voice generation directly
./test-mps-jarvis.sh
```

The performance tests will generate detailed reports comparing CPU and MPS performance for voice generation.

If you experience any issues with MPS acceleration, you can force CPU-only mode by modifying the command in `src/index.ts` to remove the `PYTORCH_ENABLE_MPS_FALLBACK=1` environment variable.
