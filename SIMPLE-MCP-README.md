# Simple Jarvis MCP for Cursor

This is a simplified version of the Jarvis MCP that doesn't rely on audio playback. It's designed to be more reliable when used with Cursor.

## Setup Instructions

1. Make sure the simple MCP is built:

   ```bash
   npx tsc src/simple-mcp.ts --outDir dist --esModuleInterop --module NodeNext --moduleResolution NodeNext
   ```

2. In Cursor, go to Settings > MCPs

3. Add a new MCP with the following command:

   ```
   node /Users/gijoe/Documents/jarvis-mcp/dist/simple-mcp.js
   ```

   (Replace the path with the absolute path to your simple-mcp.js file)

4. Save the MCP configuration

5. Restart Cursor

6. Add the following to your Cursor prompt rules:
   ```
   When a task is completed, use the speakJarvis tool with the task name to have Jarvis announce completion.
   ```

## Troubleshooting

If you're still having issues with the MCP, try the following:

1. Check the Cursor logs for error messages
2. Make sure the path to the simple-mcp.js file is correct
3. Try running the simple MCP directly from the terminal:
   ```bash
   ./start-simple-mcp.sh
   ```
4. If all else fails, you can use a text-only approach by adding this to your prompt rules:
   ```
   When a task is completed, say "Jarvis: I have completed [task] sir, is there anything else you'd like me to do."
   ```
