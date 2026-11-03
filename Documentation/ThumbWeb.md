# ThumbWeb

> Reference: Thumby Random/ThumbWeb/main.py

ThumbWeb is a text-driven browser prototype for the Thumby that focuses on lightweight navigation, local content lookup, and host-driven page loading.

## Purpose

This version of the browser uses a small search interface and a cursor UI to display content lines and links. It is designed to work with text content rather than a full HTML renderer, which keeps it practical for a tiny display.

## Main mechanics

- A keyboard interface for entering search queries
- Local page content loaded into a line-based viewer
- Clickable links represented as text entries in a list
- History tracking so users can move backward through previously visited pages
- Search and page load commands sent through a simple request flow

## Runtime model

The script listens for serial or stdin-style data, interprets text frames, and then renders them as a page. This makes it look more like a host-managed text interface than a self-contained browser engine.

> The code is intentionally simple: it treats pages as text segments and links, not as real HTML documents.

## Notes

ThumbWeb demonstrates a browser-first approach for Thumby, emphasizing minimal UI complexity and direct interaction with local or host-provided content.
