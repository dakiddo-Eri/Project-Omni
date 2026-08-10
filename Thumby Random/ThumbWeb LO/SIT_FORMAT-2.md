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

## Search: `index.sit`

There's no live search engine offline, so `/Sites/index.sit` is a
hand-written keyword map the engine scans on every search: 
(UPDATE, theres live search now, just ignore index its deleted)

```
K:<Label>=<keyword1>|<keyword2>|...=<target.sit>
```

Example:

```
# index.sit - search keyword map
K:Gooogle Home=google|gooogle|search engine=google.sit
K:Gooogle Wiki=wiki|wikipedia|encyclopedia=wiki.sit
```

A search matches if the typed query is a substring of a keyword, or a
keyword is a substring of the query — so partial and slightly-off
queries still hit. The first 6 matches become a results page
automatically; no matches shows "No results for".

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
