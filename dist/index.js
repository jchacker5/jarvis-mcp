import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { exec } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";
import player from "play-sound";
import { fileURLToPath } from "url";
import { z } from "zod";
// Get the directory name in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const audioPlayer = player();
const TEMP_DIR = path.join(os.tmpdir(), "jarvis-mcp");
// Create temp directory if it doesn't exist
if (!fs.existsSync(TEMP_DIR)) {
    fs.mkdirSync(TEMP_DIR, { recursive: true });
}
// Generate a unique filename for the audio
function getAudioFilePath() {
    const timestamp = Date.now();
    return path.join(TEMP_DIR, `jarvis-${timestamp}.wav`);
}
// Generate and play audio using the CSM model
async function generateAndPlayAudio(text) {
    return new Promise((resolve, reject) => {
        // Add a timeout to prevent hanging
        const timeout = setTimeout(() => {
            console.error("Audio generation timed out after 60 seconds");
            reject(new Error("Audio generation timed out"));
        }, 60000); // 60 second timeout (increased from 30)
        const outputPath = getAudioFilePath();
        const scriptPath = path.join(path.dirname(__dirname), "src", "voice_generator.py");
        console.log(`Generating audio for: "${text}"`);
        console.log(`Using script path: ${scriptPath}`);
        console.log(`Output path: ${outputPath}`);
        // Execute the Python script with virtual environment
        // Use absolute paths to ensure it works in any environment
        const venvPath = path.join(process.cwd(), ".venv");
        const activateCmd = process.platform === "win32"
            ? `"${path.join(venvPath, "Scripts", "activate")}"`
            : `source "${path.join(venvPath, "bin", "activate")}"`;
        // Enable MPS acceleration with fallback for operations not supported on MPS
        const command = `PYTORCH_ENABLE_MPS_FALLBACK=1 ${activateCmd} && python "${scriptPath}" --text "${text}" --output "${outputPath}"`;
        console.log(`Executing command: ${command}`);
        exec(command, (error, stdout, stderr) => {
            // Clear the timeout since the command has completed
            clearTimeout(timeout);
            if (error) {
                console.error("Error generating audio:", error);
                console.error("stderr:", stderr);
                reject(new Error(`Failed to generate audio: ${error.message}`));
                return;
            }
            console.log("Python script output:", stdout);
            if (stdout.includes("Error generating audio") ||
                stdout.includes("Error:")) {
                console.error("Error detected in Python script output:", stdout);
                reject(new Error(`Error in Python script: ${stdout}`));
                return;
            }
            if (!fs.existsSync(outputPath)) {
                console.error("Audio file was not created:", outputPath);
                reject(new Error("Audio file was not created"));
                return;
            }
            // Try different methods to play audio based on platform
            console.log(`Playing audio file: ${outputPath}`);
            try {
                // First try using play-sound
                audioPlayer.play(outputPath, (err) => {
                    if (err) {
                        console.error("Error playing audio with play-sound:", err);
                        // Try platform-specific commands as fallback
                        let playCmd = "";
                        if (process.platform === "darwin") {
                            playCmd = `afplay "${outputPath}"`;
                        }
                        else if (process.platform === "win32") {
                            playCmd = `powershell -c (New-Object Media.SoundPlayer "${outputPath}").PlaySync()`;
                        }
                        else if (process.platform === "linux") {
                            playCmd = `aplay "${outputPath}"`;
                        }
                        if (playCmd) {
                            console.log(`Trying fallback command: ${playCmd}`);
                            exec(playCmd, (playError, playStdout, playStderr) => {
                                if (playError) {
                                    console.error("Error playing audio with fallback command:", playError);
                                    console.error("stderr:", playStderr);
                                    // Even if audio playback fails, consider it a success
                                    // This allows the MCP to work even if audio can't be played
                                    console.log("Audio playback failed, but continuing anyway");
                                    // Clean up the temporary file
                                    fs.unlink(outputPath, (unlinkErr) => {
                                        if (unlinkErr) {
                                            console.warn("Failed to delete temporary audio file:", unlinkErr);
                                        }
                                        else {
                                            console.log("Temporary audio file deleted");
                                        }
                                    });
                                    resolve();
                                }
                                else {
                                    console.log("Audio played successfully with fallback command");
                                    // Clean up the temporary file
                                    fs.unlink(outputPath, (unlinkErr) => {
                                        if (unlinkErr) {
                                            console.warn("Failed to delete temporary audio file:", unlinkErr);
                                        }
                                        else {
                                            console.log("Temporary audio file deleted");
                                        }
                                    });
                                    resolve();
                                }
                            });
                        }
                        else {
                            // No fallback available, but continue anyway
                            console.log("No fallback audio playback available, continuing anyway");
                            // Clean up the temporary file
                            fs.unlink(outputPath, (unlinkErr) => {
                                if (unlinkErr) {
                                    console.warn("Failed to delete temporary audio file:", unlinkErr);
                                }
                                else {
                                    console.log("Temporary audio file deleted");
                                }
                            });
                            resolve();
                        }
                    }
                    else {
                        console.log("Audio played successfully with play-sound");
                        // Clean up the temporary file
                        fs.unlink(outputPath, (unlinkErr) => {
                            if (unlinkErr) {
                                console.warn("Failed to delete temporary audio file:", unlinkErr);
                            }
                            else {
                                console.log("Temporary audio file deleted");
                            }
                        });
                        resolve();
                    }
                });
            }
            catch (playError) {
                console.error("Exception during audio playback:", playError);
                // Even if audio playback fails, consider it a success
                // This allows the MCP to work even if audio can't be played
                console.log("Audio playback failed, but continuing anyway");
                // Clean up the temporary file
                fs.unlink(outputPath, (unlinkErr) => {
                    if (unlinkErr) {
                        console.warn("Failed to delete temporary audio file:", unlinkErr);
                    }
                    else {
                        console.log("Temporary audio file deleted");
                    }
                });
                resolve();
            }
        });
    });
}
async function main() {
    console.log("Starting Jarvis MCP server...");
    console.log(`Current working directory: ${process.cwd()}`);
    console.log(`Node.js version: ${process.version}`);
    console.log(`Platform: ${process.platform}`);
    const server = new McpServer({
        name: "JarvisMCP",
        version: "1.0.0",
    });
    // Tool to play Jarvis voice after task completion
    server.tool("speakJarvis", {
        task: z.string().optional(),
        customMessage: z.string().optional(),
    }, async ({ task, customMessage }) => {
        console.log("speakJarvis tool called with:", { task, customMessage });
        const defaultMessage = `I have completed${task ? ` ${task}` : ""} sir, is there anything else you'd like me to do.`;
        const message = customMessage || defaultMessage;
        try {
            console.log("Starting audio generation for:", message);
            await generateAndPlayAudio(message);
            console.log("Audio generation and playback completed");
            return {
                content: [{ type: "text", text: `Jarvis said: "${message}"` }],
            };
        }
        catch (error) {
            console.error("Failed to generate or play audio:", error);
            // Get detailed error message
            const errorMessage = error instanceof Error ? error.message : String(error);
            console.log("Returning success message despite error");
            // Return success message anyway to ensure the MCP works
            // even if audio generation or playback fails
            return {
                content: [
                    {
                        type: "text",
                        text: `Jarvis said: "${message}" (Note: Audio failed but message delivered)`,
                    },
                ],
            };
        }
    });
    // Start the server using stdio transport
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.log("Jarvis MCP server started...");
}
main().catch((error) => {
    console.error("Failed to start MCP server:", error);
    process.exit(1);
});
