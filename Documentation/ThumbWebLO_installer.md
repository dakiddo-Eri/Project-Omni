# ThumbWebLO Installer and PC Deployer

This document describes the current ThumbWebLO deployment tools and the named-pack manifest. The installer folder contains the host-side deployer [fire.py](../Thumby%20Random/ThumbWebLO_installer/fire.py), the Thumby browser app [ThumbWebLO.py](../Thumby%20Random/ThumbWebLO_installer/ThumbWebLO.py), the site library under **Sites/**, and [manifest.txt](../Thumby%20Random/ThumbWebLO_installer/manifest.txt).

## What it does

The PC deployer uploads the browser app and selected `.sit` site files to a connected Thumby using `mpremote`. Sites are grouped into named packs so a user can deploy all content or choose only selected groups. The app and sites are placed in the device's ThumbWebLO game folder; the browser reads sites from **/Games/ThumbWebLO/Sites/**.

## Requirements and running

- A computer with Python 3 and the `mpremote` package installed. If needed, install it with `pip install mpremote`.
- A Thumby connected to the computer and available to `mpremote`.
- The deployer, browser app, manifest, and **Sites/** content kept together in the installer folder.

Run the deployer from the installer folder with:

```sh
python3 fire.py
```

The deployer checks that `mpremote` is available, reads the manifest, and displays the available packs. Answer `y` to deploy all packs or `n` and enter comma-separated pack numbers to choose packs. The browser app is uploaded whenever its local source file exists, independently of the selected site packs. Site files are then copied into the matching device-side paths.

## Manifest format

Each section header is a pack name in square brackets. The lines beneath it are site paths relative to the installer's **Sites/** folder. Blank lines and lines beginning with `#` are ignored. Subfolders are supported, and backslashes in manifest entries are converted to forward slashes by the deployer.

For example, a site in a `news` subfolder is listed relative to the **Sites/** folder:

```text
# Comment lines are allowed
[News Pack]
news/article.sit
news/updates.sit

[Games Pack]
games/puzzle.sit
```

Keep the path spelling, capitalization, and folder names identical to the real files. The manifest does not relocate or rename files: the relative folder structure is reproduced under the device's **Sites/** directory. The current manifest defines Wiki, News, Tech, Important, Poetry, Games, Web and Media, Finance, Personal Sites, and Misc packs.

## Deployment behavior

1. [fire.py](../Thumby%20Random/ThumbWebLO_installer/fire.py) parses the manifest in order and reports the number of entries in each pack.
2. It creates the device-side ThumbWebLO and Sites directories, then uploads [ThumbWebLO.py](../Thumby%20Random/ThumbWebLO_installer/ThumbWebLO.py) as the browser program.
3. It creates any nested destination directories needed by the selected site paths and copies each selected file.
4. It prints a warning and skips a manifest entry if its local source file is missing. A failed `mpremote` copy stops the deployer with an error.

Deployment is additive: choosing fewer packs does not delete files already on the Thumby. To update a site, deploy its pack again. A pack that includes [home.sit](../Thumby%20Random/ThumbWebLO_installer/Sites/home.sit) supplies the browser's home page; when that page is absent, the browser falls back to a directory listing.

## Troubleshooting and notes

- **No connection or copy failure:** confirm the Thumby is connected and recognized by `mpremote`; retry the deployer after resolving the reported command error. Remember, no other program must be currently accesing the Thumby for it to work, eg. connected to the Web Thumby Code Editor.
- **A site is skipped:** compare its manifest entry to the exact file name and relative path beneath **Sites/**, including case and slashes. The current code warns about missing files but does not validate the entire manifest before deployment.
- **Unexpected empty pack:** the parser starts with a `Default Pack` before reading named sections. Since the current manifest puts its files under named sections, this may appear as an empty first choice; use the displayed pack numbers for the named packs.
- **Old files remain on the device:** this is expected. The deployer copies selected content but does not remove unselected or obsolete site files.

This folder currently provides a host-side deployer, not a Thumby-resident pack installer. The [fire.py](../Thumby%20Random/ThumbWebLO_installer/fire.py) script requires a computer and `mpremote`; [ThumbWebLO.py](../Thumby%20Random/ThumbWebLO_installer/ThumbWebLO.py) is the app that runs on the Thumby.
