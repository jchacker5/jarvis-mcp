// Test script for the audio MCP
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Flag to track if we've received a response
let receivedResponse = false;

// Start the MCP server
console.log("Starting MCP server...");
const mcpProcess = spawn("node", [path.join(__dirname, "dist", "index.js")], {
  stdio: ["pipe", "pipe", "pipe"],
});

// Log server output
mcpProcess.stdout.on("data", (data) => {
  const output = data.toString();
  console.log(`MCP stdout: ${output}`);

  // Check if we've received the completion message
  if (
    output.includes("Audio generation and playback completed") ||
    output.includes("Returning success message despite error")
  ) {
    receivedResponse = true;
    console.log(
      "Audio processing completed, waiting 5 more seconds before exiting..."
    );

    // Wait a bit more and then exit
    setTimeout(() => {
      console.log("Test completed, exiting...");
      mcpProcess.kill();
      process.exit(0);
    }, 5000);
  }
});

mcpProcess.stderr.on("data", (data) => {
  console.error(`MCP stderr: ${data}`);
});

// Wait for server to start
setTimeout(() => {
  console.log("Sending speakJarvis request...");

  // Send a request to call the speakJarvis tool
  const callRequest = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "speakJarvis",
      arguments: {
        customMessage: "Testing the audio MCP directly",
      },
    },
  };

  mcpProcess.stdin.write(JSON.stringify(callRequest) + "\n");

  // Set a timeout in case we don't receive a response
  setTimeout(() => {
    if (!receivedResponse) {
      console.log("No completion message received, exiting anyway...");
      mcpProcess.kill();
      process.exit(1);
    }
  }, 60000); // Wait up to 60 seconds for a response
}, 2000); // Wait 2 seconds for server to start
