# Cursor Sound MCP

A Model Context Protocol (MCP) implementation that plays sound effects after Cursor AI completes code generation. This MCP integrates with Cursor to provide audio feedback for a more interactive coding experience.

## Features

- Plays a sound effect when Cursor completes code generation
- Uses the Model Context Protocol (MCP) for standardized integration
- Configurable sound effects

## Installation

1. Install dependencies:
```bash
npm install
```

2. Add your sound effects:
Place your sound files in the `sounds` directory. The default expected sound is:
- `sounds/completion.mp3` - Played after code generation

You can find free sound effects on freesound.org.

3. Build the project:
```bash
npm run build
```

## Usage

Run the MCP server:
```bash
npm start
```

The server will start and listen for events from Cursor through the stdio transport.

## Configuration

The sound effects and volume can be customized by:
1. Replacing the sound files in the `sounds` directory
2. Modifying the sound file paths in `src/index.ts`

## Development

For development with auto-recompilation:
```bash
npm run dev
```
