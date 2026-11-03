# Kitmen

> Reference: Thumby Random/Kitmen/Kitmen.py

Kitmen is a tile-based exploration game that runs on the Thumby. It uses a procedurally generated map, animated sprite movement, and simple encounter logic inside a compact world.

**The game itself is unfinished and do not expect great quality cuz its very buggy yea.**

## Purpose

The project creates a small action-exploration experience in which the player moves through a world made from tiles and encounters special blocks or enemy-like triggers while traversing the map.

## Game systems

- tile map generation and camera tracking
- player sprite animation for idle and walking states
- blinking behavior and map exploration loop
- eviler block spawning and trigger checking
- world rendering with sprite blits and rectangles

## World structure

The map is built from a grid with different tile types, including grass-like and pattern-filled areas. The camera follows the player so the world feels larger than the visible screen area.

> This design is typical of lightweight handheld games: a compact world, limited motion, and direct tile-based rendering.

## Notes

The game is highly experimental and built around simple mechanics rather than large content. It is a good example of how the project uses minimal display operations and procedural generation to squeeze a more complete game into the Thumby screen size.
