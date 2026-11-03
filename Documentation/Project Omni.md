# Project Omni

> Reference: README.md and the project root layout

Project Omni is a small collection of experimental Thumby-focused software and operating-system prototypes. The codebase blends lightweight utilities, local browsing tools, mini-games, and an evolving OS concept built around low-memory hardware.

## Overview

The repository is organized around a central idea: make useful software that can run on constrained hardware while staying lightweight, readable, and flexible. The projects in this folder range from a full-screen operating system and browser to a benchmark suite and audio-oriented tools.

## Main code areas

- House 26 OS: a bootable-style OS shell with home navigation, music, notes, and utility apps
- ThumbWeb: a text browser for Thumby screens, focused on browsing local site content and performing searches
- ThumbWebLO: a streamlined local site browser with a compact navigation model
- ThumbWebLO-Japanese: a Japanese-language variant with custom glyph support
- Thumby Benchmark: a hardware performance measuring tool for empirical testing
- Thumby Surf: an endless surfing runner with score tracking and audio
- MidiPlayer: a MIDI playback app for Thumby using custom synth and MIDI parsing
- Kitmen: a tile-based exploration game with procedural map generation and movement

## Design goals

- Keep app logic small enough for low-memory micro devices
- Favor direct hardware control over heavy abstraction
- Support game-like interaction, browsing, and utility tasks on compact screens
- Build a developer-friendly environment for experimentation and iteration

## Repository notes

> The project is clearly experimental and in active development.

This repository is best understood as a code playground for Thumby software experiments and a foundation for further OS and device tooling.
