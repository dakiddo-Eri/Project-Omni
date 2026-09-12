# .sit file format (ThumbWeb offline)

A `.sit` file is plain text. One directive per line. No numeric offsets,
no binary layout, no build step — write it in any text editor and drop
it in `/Sites/` on the device.

## Directives

| Prefix | Meaning |
|---|---|
| `T:<text>` | A line of displayed text. Keep it to ~12 characters — that's the physical screen width; anything longer is clipped when rendered. |
| `L:<target>` | Turns the **previous** `T:` line into a link. `<target>` is a filename inside `/Sites/` (e.g. `L:about.sit`). |
| `L:SEARCH` | Special case: instead of loading a file, this opens the on-device keyboard for a new search — use it to put a search box inside a page's body, not just the top bar. |
| `L:HOME` | Jumps straight back to the home page, same as if history were empty. |
| `L:BACK` | Same as pressing the B button — pops one page off history (or goes home if there's nothing to pop). |
| `# comment` | Ignored. Use freely for notes. |
| `A: <frame>` | Animation, you make one frame separated by pipes and another frame which switched from one frame to another|
| *(blank line)* | Ignored. |
| *(anything else)* | Ignored. Reserved for future directives — old engines skip lines they don't understand instead of breaking. |

## Example: `home.sit`

```
# home.sit - boots on startup
T:ThumbWeb
T:offline demo
T:------------
T:Search
L:SEARCH
T:Open Gooogle
L:google.sit
```

##Example: Animation
```
A:  (o<     |  (o>     
A: ~(== )   | ~( ==)   
A:  J  J    |   L  L
```

## Layout conventions

- Site files live flat in `/Sites/`. Links are just filenames within
  that folder (`L:google.sit`), or an absolute path if you want to
  nest folders (`L:/Sites/news/tech.sit`).
- If `/Sites/home.sit` doesn't exist, the device automatically lists
  every `.sit` file it finds as a fallback home page — you always have
  something to click on.
- Keep individual `.sit` files small (well under a few KB). The engine
  reads them one line at a time, but the whole parsed page still lives
  in RAM while you're on it, and the Original Thumby's flash storage
  is limited.
