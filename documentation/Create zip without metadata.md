In Windows 11, how to create a zip file that has all the individual file metadata erased in the zip?



Windows’ built‑in “Send to → Compressed (zipped) folder” has no way to strip the timestamps and other NTFS metadata from each entry—you’ll need a tool like 7‑Zip.

1. **Install 7‑Zip** if you haven’t already (from [https://7‑zip.org](https://7%E2%80%91zip.org)).

2. **Open a Command Prompt or PowerShell** and run:
   
   ```powershell
   "C:\Program Files\7-Zip\7z.exe" a `
     -tzip "C:\path\to\archive.zip" `
     "C:\path\to\files\*" `
     -mtc=off
   ```
   
   - `a` tells 7‑Zip to **add** files to an archive.
   
   - `-tzip` makes it use the standard ZIP format.
   
   - `-mtc=off` disables storing **all** NTFS timestamps (modification, creation & last‑access) in the ZIP [SourceForge](https://sourceforge.net/p/sevenzip/discussion/45798/thread/bae27baf/)[Stack Overflow](https://stackoverflow.com/questions/27136783/7zip-produces-different-output-from-identical-input).

  If you also want maximum compression (or any other level), tack on `-mx=9` (or `-mx=0…9`).

That archive will contain only file names and file data—no individual file timestamps will be preserved.


