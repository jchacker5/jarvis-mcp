import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import player from 'play-sound';

const audioPlayer = player();
const SYSTEM_SOUND = '/System/Library/Sounds/Glass.aiff'; // macOS system sound

async function main() {
  const server = new McpServer({
    name: 'CursorSoundMCP',
    version: '1.0.0'
  });

  // Tool to play sound after code generation
  server.tool(
    'playCompletionSound',
    {},
    async () => {
      try {
        // Play macOS system sound
        audioPlayer.play(SYSTEM_SOUND, (err: Error | null) => {
          if (err) console.error('Error playing sound:', err);
        });
        return {
          content: [{ type: 'text', text: 'Played completion sound' }]
        };
      } catch (error) {
        console.error('Failed to play sound:', error);
        return {
          content: [{ type: 'text', text: 'Failed to play sound' }]
        };
      }
    }
  );

  // Start the server using stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.log('Cursor Sound MCP server started...');
}

main().catch(error => {
  console.error('Failed to start MCP server:', error);
  process.exit(1);
});
