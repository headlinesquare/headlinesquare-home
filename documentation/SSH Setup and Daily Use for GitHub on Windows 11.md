**SSH Setup & Daily Use for GitHub on Windows 11**

---

### 1. Generate SSH key (one-time)

Open **PowerShell** (or Anaconda Prompt if you prefer):

```powershell
ssh-keygen -t ed25519 -C "your_github_email@example.com"
```

- Press **Enter** to accept the default path (`C:\Users\<you>\.ssh\id_ed25519`).

- For no prompts when pushing: press **Enter** again for empty passphrase.

---

### 2. Add the public key to GitHub

Show your public key:

```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
```

Copy it, then on GitHub:

- **Profile picture → Settings → SSH and GPG keys → New SSH key**

- **Type:** Authentication key

- Paste the key and save.

---

### 3. Trust and test GitHub SSH

```powershell
ssh -T git@github.com
```

Type **yes** if prompted to trust GitHub’s host key.  
Success looks like:

```
Hi USERNAME! You've successfully authenticated, but GitHub does not provide shell access.
```

---

### 4. Use SSH for your repos

From inside each repo folder:

```powershell
git remote set-url origin git@github.com:USERNAME/REPO.git
git remote -v   # confirm it shows git@github.com:...
```

---

### 5. Make it automatic

If your key has **no passphrase** → nothing else needed.

If your key **has a passphrase** → load it into the OpenSSH agent so you’re not prompted:

```powershell
# Enable and start the agent (one-time)
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent

# Add your key (once per logon session)
ssh-add $env:USERPROFILE\.ssh\id_ed25519
ssh-add -l    # should list your key
```

---

### 6. Daily usage

From your repo folder:

```powershell
git add .
git commit -m "Update site content"
git push
```

No username/password prompts should appear.

---

### 7. Quick troubleshooting

- **Check remote**: `git remote -v`

- **Test SSH**: `ssh -T git@github.com`

- **List loaded keys**: `ssh-add -l`

- **Reload key**: `ssh-add $env:USERPROFILE\.ssh\id_ed25519`
