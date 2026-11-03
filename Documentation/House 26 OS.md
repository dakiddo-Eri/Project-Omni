# House 26 OS

> Reference: House 26 OS.py

House 26 OS is a Thumby operating-system prototype designed around a compact home interface, boot animation, and a set of built-in apps for music, reading, notes, drawing, and system-style utilities.

## Purpose

This project behaves like a small OS shell rather than a single game. It includes a custom boot sequence, random status messages, and an app-selection style interface that runs on a the Thumby.

## Main features

- Boot animation with themed startup messages
- Home screen with rotating daily text
- Music player interface with selectable tracks
- App categories such as notes, reading, info, calculator, drawing, and gallery
- System-like input handling for directional and action buttons
- Lightweight rendering and paging helpers

## Core behavior

The code uses a simple event loop with button polling and screen updates. It manages home scrolling, UI state changes, and audio playback through thumby hardware primitives.

> The project clearly targets the original Thumby display and button layout, using short text rendering, minimal memory usage, and direct hardware access for smooth operation.

## Notes

This is not a polished consumer OS; it is a device-focused prototype that emphasizes personality, experimentation, and compact UI design. The file includes a number of whimsical status strings and debug-style comments, which matches the creative nature of the project.
