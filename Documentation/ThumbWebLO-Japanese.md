# ThumbWebLO-Japanese

> Reference: Thumby Random/ThumbWebLO-Japanese/ThumbWebLO-Japanese.py

ThumbWebLO-Japanese is the Japanese-language variant of ThumbWebLO. It keeps the same site-browsing concept but adds custom glyph rendering and supports Japanese text through a font file.

## Purpose

This project extends the local browser idea for Japanese content. Instead of using a basic Latin-only display path, it includes custom font loading and kana handling so the browser can render Japanese characters inside the same tiny screen format.

## Main features

- Loads a Japanese bitmap font from jpy.fnt
- Detects kana characters and draws them with 8x8 glyphs
- Parses .sit files with Japanese-friendly page text
- Supports search, directory listing, and link navigation
- Keeps the same compact browser layout as the original ThumbWebLO

## Rendering approach

The code reads a custom font format, decodes glyphs, and draws them as bitmaps onto the display. This allows a wider character set without replacing the overall browser logic.

> The browser remains text-first and lightweight, but it expands its display capability to support East Asian scripts.

## Notes

This variant is a localization and compatibility layer on top of the same browser concept, demonstrating how the project adapts core tools for other languages and display needs.
