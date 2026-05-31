# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **npm workspace** for the Brilliant SDK for WebBluetooth (TypeScript), providing integration with Brilliant Labs AR devices (Frame and Halo smart glasses) from browser environments. It contains 3 packages under `packages/`.

## Commands

```bash
npm install                    # install all dependencies (run from workspace root or package dir)
npm run build                  # build dist/ (run from a package directory)
npm run dev                    # start Vite dev server for the example app
npm run docs:api               # generate TypeDoc API docs
```

Publishing to npm (publish in dependency order):
```bash
npm publish --access public    # from each package directory
# Order: brilliant-ble → brilliant-msg → brilliant-sdk
```

The `dist/` files are committed to the repository and must be rebuilt before publishing.

## Architecture

The SDK is organized in layers:

**`brilliant-ble`** — Low-level WebBluetooth connection layer. Handles device scanning, connection, MTU-aware packet splitting, and characteristic I/O. Exposes `BrilliantBle` and `BrilliantDeviceType`.

**`brilliant-msg`** — Application-level messaging protocol. Defines TX (host → device) and RX (device → host) message types. TX messages serialize to `Uint8Array` for BLE transmission. RX messages are parsed from incoming byte streams. Each message type has a corresponding Lua script in `src/lua/` that runs on the device. Both full and `.min.lua` versions are included.

**`brilliant-sdk`** — Meta-package (`src/index.ts` re-exports everything from `brilliant-ble` and `brilliant-msg`) for a single install.

## Key Design Patterns

- **Message protocol**: Each TX message type has a unique message code (e.g. `0x0d`). The BLE layer handles chunking based on negotiated MTU. Lua scripts on the device reassemble and render.
- **Async**: All device interaction uses `Promise`/`async`/`await` throughout.
- **Lua pairing**: Every message type in `brilliant-msg` has a corresponding `.lua` and `.min.lua` file in `src/lua/`. When adding new message types, both the TypeScript class and the Lua script must be updated together.
- **Build output**: Vite produces both ESM (`*.es.js`) and UMD (`*.umd.js`) bundles plus TypeScript declaration files in `dist/`.
