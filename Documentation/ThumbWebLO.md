# ThumbWebLO

> Reference: Thumby Random/ThumbWebLO/main.py

ThumbWebLO is a small local web-style browser for the Thumby. It loads site content from a structured text format, lets the user browse pages, search local files, and navigate through a lightweight list-based UI.

## Purpose

The app is designed to present text-based documents and links on a tiny screen. It reads .sit files, turns them into navigable pages, and handles search, directory browsing, and back navigation.

## Key functionality

- Reads local site files from /Games/ThumbWebLO/Sites/
- Parses page entries using T:, A:, and L: record types
- Searches for matching site files by name
- Shows page lines and clickable links on a constrained display
- Supports history tracking and return to previous pages
- Renders a compact keyboard UI for query entry

## Data model

Site data is stored in a simple custom format where each line can represent:

- text content
- animated line frames
- links associated with a given row

This keeps the browser lightweight and easy to maintain without a full web engine.

> The browser is intentionally minimal: it treats each page as a list of lines and links rather than a full HTML renderer.

## Typical flow

1. App starts on the home page or directory listing
2. User searches or selects a site
3. The code loads the page file and maps text rows to clickable links
4. The cursor highlights entries and triggers navigation
5. Back-history allows fast return to previous pages

## Engine
The entire libary of sites in this program is run using a custom programming language called LO--. LO-- is a lightweight programming language just for the purpose of displaying text based and a bit of animation into .sit files (not the compression one, our custom one). 

> See LO-- programming language documentation for more.

## Notes

ThumbWebLO is effectively a compact offline browsing system for microdevices, built for exploration and local content rather than full internet browsing.
