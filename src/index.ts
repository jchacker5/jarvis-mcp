import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { exec } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { z } from "zod";

// Get the directory name in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const AUDIO_DIR = path.join(path.dirname(__dirname), "audio");
const VOICE_GENERATOR_PATH = path.join(
  path.dirname(__dirname),
  "src",
  "mlx_voice_generator.py"
);

// Ensure audio directory exists
if (!fs.existsSync(AUDIO_DIR)) {
  fs.mkdirSync(AUDIO_DIR, { recursive: true });
}

/**
 * Generate a unique filename for the audio file
 * @returns {string} Path to the audio file
 */
function getAudioFilePath(): string {
  const timestamp = Date.now();
  return path.join(AUDIO_DIR, `jarvis_${timestamp}.wav`);
}

/**
 * Generate audio using the MLX voice generator
 * @param {string} text - Text to convert to speech
 * @param {string} voice - Voice style to use
 * @param {number} speed - Speech speed multiplier
 * @returns {Promise<string>} Path to the generated audio file
 */
async function generateAudio(
  text: string,
  voice: string = "af_heart",
  speed: number = 1.0
): Promise<string> {
  return new Promise((resolve, reject) => {
    const outputPath = getAudioFilePath();

    console.log(`Generating audio for: "${text}"`);
    console.log(`Using voice: ${voice}, speed: ${speed}`);

    // Activate virtual environment and run Python script
    const venvPath = path.join(process.cwd(), ".venv");
    const activateCmd =
      process.platform === "win32"
        ? `"${path.join(venvPath, "Scripts", "activate")}"`
        : `source "${path.join(venvPath, "bin", "activate")}"`;

    // Command to generate audio
    const command = `${activateCmd} && python "${VOICE_GENERATOR_PATH}" --text "${text}" --output "${outputPath}" --voice "${voice}" --speed ${speed}`;

    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error("[Voice Generator Error]", stderr);
        console.error(`Failed to generate audio. Exit code: ${error.code}`);
        console.error(`Stdout: ${stdout}`);
        console.error(`Stderr: ${stderr}`);
        reject(new Error(`Failed to generate audio. Exit code: ${error.code}`));
        return;
      }

      if (stdout.includes("Error")) {
        console.error("[Voice Generator Error]", stdout);
        reject(new Error(`Error in voice generator: ${stdout}`));
        return;
      }

      if (!fs.existsSync(outputPath)) {
        console.error("Audio file was not created:", outputPath);
        reject(new Error("Audio file was not created"));
        return;
      }

      console.log(`Audio generated successfully: ${outputPath}`);
      resolve(outputPath);
    });
  });
}

/**
 * Play the generated audio file
 * @param {string} audioPath - Path to the audio file
 * @returns {Promise<void>}
 */
async function playAudio(audioPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    console.log(`Playing audio: ${audioPath}`);

    let playCommand = "";
    if (process.platform === "darwin") {
      playCommand = `afplay "${audioPath}"`;
    } else if (process.platform === "win32") {
      playCommand = `powershell -c (New-Object Media.SoundPlayer "${audioPath}").PlaySync()`;
    } else if (process.platform === "linux") {
      playCommand = `aplay "${audioPath}"`;
    } else {
      console.warn("Unsupported platform for audio playback");
      resolve();
      return;
    }

    exec(playCommand, (error) => {
      if (error) {
        console.error("Error playing audio:", error);
        reject(error);
        return;
      }

      console.log("Audio playback complete");
      resolve();
    });
  });
}

/**
 * Clean up the audio file after playback
 * @param {string} audioPath - Path to the audio file
 */
function cleanupAudio(audioPath: string): void {
  try {
    fs.unlinkSync(audioPath);
    console.log(`Cleaned up audio file: ${audioPath}`);
  } catch (error) {
    console.error("Error cleaning up audio file:", error);
  }
}

async function main() {
  console.log("Starting Jarvis MCP server with MLX-Audio...");
  console.log(`Current working directory: ${process.cwd()}`);
  console.log(`Node.js version: ${process.version}`);
  console.log(`Platform: ${process.platform}`);

  const server = new McpServer({
    name: "JarvisMCP",
    version: "1.0.0",
  });

  // Tool to play Jarvis voice after task completion
  server.tool(
    "speakJarvis",
    {
      task: z.string().optional(),
      customMessage: z.string().optional(),
      voice: z.string().optional(),
      speed: z.number().optional(),
    },
    async ({ task, customMessage, voice, speed }) => {
      console.log("speakJarvis tool called with:", {
        task,
        customMessage,
        voice,
        speed,
      });

      const defaultMessage = `I have completed${
        task ? ` ${task}` : ""
      } sir, is there anything else you'd like me to do.`;
      const message = customMessage || defaultMessage;

      try {
        console.log("Starting MLX audio generation for:", message);

        // Generate audio directly (no need to forward to another server)
        const audioPath = await generateAudio(
          message,
          voice || "af_heart",
          speed || 1.0
        );

        // Play the audio
        await playAudio(audioPath);

        // Clean up the audio file
        cleanupAudio(audioPath);

        console.log("MLX audio generation and playback completed");

        return {
          content: [
            {
              type: "text",
              text: `Jarvis said: "${message}" (Audio played successfully)`,
            },
          ],
        };
      } catch (error) {
        console.error("Failed to generate or play audio:", error);

        // Get detailed error message
        const errorMessage =
          error instanceof Error ? error.message : String(error);

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
    }
  );

  // Start the server using stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.log("Jarvis MCP server started with integrated MLX-Audio support...");
}

main().catch((error) => {
  console.error("Failed to start MCP server:", error);
  process.exit(1);
});
