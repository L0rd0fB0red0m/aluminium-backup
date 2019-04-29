# Aluminium Backup - Automatic backup and restore

All information is to be found on the [DFG-Site](https://www.dfglfa.net/Informatique/bac2019/remy).


## Guide:
### Prerequesites:
* Python 3 (duh)
* The following python3 libraries: `PyQt5, threading, sys, shutil, os, psutil, json, crontab, zipfile, pyAesCrypt, datetime` (install them through pip)


### Usage:
To launch the program, execute `python3 main.py` or double-click the one-file-executable which comes with every version. It also has the advantage of bundling all the necessary dependencies. From there every thing should be rather intuitive: switch between Backup and Restore, change settings, set options and launch the process.

### Features:
The outstanding feature of this tool is that it allows the user to run their own code to select specific files to back up. This feature gets enabled once a "generator-script" is selected in the Backup section.
The selected script must satisfy certain criteria: see
my gists for examples:
[1](https://gist.github.com/L0rd0fB0red0m/bb3f301a8c6253a12eb88899062c38f4),
[2](https://gist.github.com/L0rd0fB0red0m/be4a5f8eb15fdf3baa4d19395912ca22),
[3](https://gist.github.com/L0rd0fB0red0m/66cf790dea366e4ce408cfa71b8f03ae).


## Troubleshooting
Most errors are cleanly reported through dialogs and are caught before they crash the program. If you notice a flaw (ie. crashes), please let me know. When copying files, errors may occur due to the usage of threading. These are also caught and reported at the end of each run. It seems that __AlB__ particularly struggles with symlinks and already compressed files. Proprietary file-formats sometimes also seem to cause trouble, looks as if `shutil` doesn't like them. You can always try to rerun the programm with fewer files, or manually copy the remaining errors.

### Fix it yourself:
While backing up, __AlB__ copies the underlying folder-structure, which also serves as a memory. This means you can easily restore a particular file yourself without using the programm altogether. Same goes for adding files to an existing backup: simply copy it where it should belong and it will be picked up Automatically on restore.
