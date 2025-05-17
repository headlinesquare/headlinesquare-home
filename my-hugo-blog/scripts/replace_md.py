
import os

old = "This is an experimental project."
new = "This is an experimental AI project."

for root, _, files in os.walk("."):
    for fname in files:
        if fname.endswith(".md"):
            path = os.path.join(root, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            if old in text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text.replace(old, new))
                print(f"Updated: {path}")
