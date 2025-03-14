import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
async function main() {
    console.log("Starting Simple Jarvis MCP server...");
    const server = new McpServer({
        name: "SimpleJarvisMCP",
        version: "1.0.0",
    });
    // Simple tool that just returns a message
    server.tool("speakJarvis", {
        task: z.string().optional(),
        customMessage: z.string().optional(),
    }, async ({ task, customMessage }) => {
        console.log("speakJarvis tool called with:", { task, customMessage });
        const defaultMessage = `I have completed${task ? ` ${task}` : ""} sir, is there anything else you'd like me to do.`;
        const message = customMessage || defaultMessage;
        console.log("Jarvis would say:", message);
        // Just return the message
        return {
            content: [{ type: "text", text: `Jarvis said: "${message}"` }],
        };
    });
    // Start the server using stdio transport
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.log("Simple Jarvis MCP server started...");
}
main().catch((error) => {
    console.error("Failed to start MCP server:", error);
    process.exit(1);
});
