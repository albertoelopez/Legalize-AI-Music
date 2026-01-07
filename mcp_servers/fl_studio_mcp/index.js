#!/usr/bin/env node

/**
 * FL Studio MCP Server
 * Provides tools for automating FL Studio on Windows desktop
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import robot from "robotjs";
import windowManager from "node-window-manager";

const { Window } = windowManager;

class FLStudioMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: "fl-studio-mcp",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
    this.flWindow = null;
  }

  setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "fl_studio_find_window",
          description: "Find and focus FL Studio window",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "fl_studio_click",
          description: "Click at specific coordinates in FL Studio",
          inputSchema: {
            type: "object",
            properties: {
              x: {
                type: "number",
                description: "X coordinate",
              },
              y: {
                type: "number",
                description: "Y coordinate",
              },
              button: {
                type: "string",
                description: "Mouse button (left, right, middle)",
                enum: ["left", "right", "middle"],
                default: "left",
              },
            },
            required: ["x", "y"],
          },
        },
        {
          name: "fl_studio_keyboard",
          description: "Send keyboard input to FL Studio",
          inputSchema: {
            type: "object",
            properties: {
              keys: {
                type: "string",
                description: "Keys to type or hotkey (e.g., 'ctrl+s', 'enter')",
              },
            },
            required: ["keys"],
          },
        },
        {
          name: "fl_studio_drag_drop_midi",
          description: "Drag and drop MIDI file into FL Studio",
          inputSchema: {
            type: "object",
            properties: {
              midi_path: {
                type: "string",
                description: "Path to MIDI file",
              },
              drop_x: {
                type: "number",
                description: "X coordinate to drop MIDI",
              },
              drop_y: {
                type: "number",
                description: "Y coordinate to drop MIDI",
              },
            },
            required: ["midi_path", "drop_x", "drop_y"],
          },
        },
        {
          name: "fl_studio_get_window_info",
          description: "Get FL Studio window position and size",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "fl_studio_take_screenshot",
          description: "Take screenshot of FL Studio window",
          inputSchema: {
            type: "object",
            properties: {
              output_path: {
                type: "string",
                description: "Path to save screenshot",
              },
            },
            required: ["output_path"],
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "fl_studio_find_window":
            return await this.findFLStudioWindow();

          case "fl_studio_click":
            return await this.clickAtPosition(args.x, args.y, args.button || "left");

          case "fl_studio_keyboard":
            return await this.sendKeyboard(args.keys);

          case "fl_studio_drag_drop_midi":
            return await this.dragDropMIDI(args.midi_path, args.drop_x, args.drop_y);

          case "fl_studio_get_window_info":
            return await this.getWindowInfo();

          case "fl_studio_take_screenshot":
            return await this.takeScreenshot(args.output_path);

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${error.message}`,
            },
          ],
        };
      }
    });
  }

  async findFLStudioWindow() {
    const windows = windowManager.getWindows();
    this.flWindow = windows.find(
      (win) =>
        win.getTitle().includes("FL Studio") ||
        win.getTitle().includes("Image-Line")
    );

    if (!this.flWindow) {
      throw new Error("FL Studio window not found");
    }

    this.flWindow.bringToTop();
    const bounds = this.flWindow.getBounds();

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            title: this.flWindow.getTitle(),
            bounds: bounds,
          }, null, 2),
        },
      ],
    };
  }

  async clickAtPosition(x, y, button = "left") {
    if (!this.flWindow) {
      await this.findFLStudioWindow();
    }

    const bounds = this.flWindow.getBounds();
    const absoluteX = bounds.x + x;
    const absoluteY = bounds.y + y;

    robot.moveMouse(absoluteX, absoluteY);
    robot.mouseClick(button);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            clicked_at: { x: absoluteX, y: absoluteY },
            button: button,
          }, null, 2),
        },
      ],
    };
  }

  async sendKeyboard(keys) {
    if (!this.flWindow) {
      await this.findFLStudioWindow();
    }

    this.flWindow.bringToTop();

    // Handle special key combinations
    if (keys.includes("+")) {
      const parts = keys.split("+");
      const modifiers = parts.slice(0, -1);
      const key = parts[parts.length - 1];

      modifiers.forEach(mod => robot.keyToggle(mod.trim(), "down"));
      robot.keyTap(key.trim());
      modifiers.forEach(mod => robot.keyToggle(mod.trim(), "up"));
    } else {
      robot.keyTap(keys);
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            keys_sent: keys,
          }, null, 2),
        },
      ],
    };
  }

  async dragDropMIDI(midiPath, dropX, dropY) {
    // This is a simplified version - actual implementation would need
    // OS-specific file drag-drop handling
    if (!this.flWindow) {
      await this.findFLStudioWindow();
    }

    const bounds = this.flWindow.getBounds();
    const absoluteX = bounds.x + dropX;
    const absoluteY = bounds.y + dropY;

    // Open file browser with Ctrl+O
    robot.keyToggle("control", "down");
    robot.keyTap("o");
    robot.keyToggle("control", "up");

    await this.sleep(1000);

    // Type file path
    robot.typeString(midiPath);
    robot.keyTap("enter");

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            midi_path: midiPath,
            note: "File open dialog triggered - manual confirmation may be needed",
          }, null, 2),
        },
      ],
    };
  }

  async getWindowInfo() {
    if (!this.flWindow) {
      await this.findFLStudioWindow();
    }

    const bounds = this.flWindow.getBounds();

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            title: this.flWindow.getTitle(),
            bounds: bounds,
            isVisible: this.flWindow.isVisible(),
            isMinimized: this.flWindow.isMinimized(),
          }, null, 2),
        },
      ],
    };
  }

  async takeScreenshot(outputPath) {
    if (!this.flWindow) {
      await this.findFLStudioWindow();
    }

    const bounds = this.flWindow.getBounds();
    const screenshot = robot.screen.capture(
      bounds.x,
      bounds.y,
      bounds.width,
      bounds.height
    );

    // Save screenshot (simplified - would need image library in real implementation)
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            output_path: outputPath,
            dimensions: { width: bounds.width, height: bounds.height },
            note: "Screenshot capture simulated - full implementation requires image library",
          }, null, 2),
        },
      ],
    };
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("FL Studio MCP server running on stdio");
  }
}

const server = new FLStudioMCPServer();
server.run().catch(console.error);
