# Quick Start Guide: Setting Up a Hugo Blog with Codeberg Pages on Windows 11

This guide covers every step—from installing Git and Hugo to creating your site and deploying it live with Codeberg Pages.

---

## Prerequisites

- **Windows 11** operating system.
- **Anaconda** installed (for a comfortable terminal environment).
- A web browser.

---

# 1. Install Git

**a. Download and Install Git**

1. Visit the [Git for Windows website](https://git-scm.com/download/win).

2. Download the installer.

3. Run the installer:
- **PATH
   Option:** Choose **"Git from the command line and also from 3rd-party software"**.

- **Line
   Endings:** Select **"Checkout Windows-style, commit Unix-style line endings"**.

- Leave
   other defaults unless you have special needs.
5. Complete
   the installation.

**b. Verify Git Installation**

Open **Anaconda Prompt** and run:

```powershell
git --version
```

You should see a version string (e.g., `git version 2.49.0.windows.1`).

---

## 2. Install Hugo (Extended Version)

**a. Download Hugo Extended**

1. Go to the [Hugo Releases page](https://github.com/gohugoio/hugo/releases).
2. Download the latest `hugo_extended_0.xx.x_Windows-64bit.zip` file.
3. Extract the contents to a folder (e.g., `C:\Hugo\bin`).

**b. Add Hugo to the System PATH**

1. Press `Win + S`, type "environment variables” and open it.
2. Under **System Variables**, select Path → **Edit** → **New** and add `C:\Hugo\bin`.
3. Click **OK** to save your changes.

**c. Verify Hugo Installation**

In **Anaconda Prompt**, run:

```powershell
hugo version
```

You should see something like `hugo v0.xx.x+extended` ....

---

**3. Create Your Hugo Blog**

**a. Create a New Site**

In **Anaconda Prompt**, navigate to your desired root project folder like `Blog` and run:

```powershell
hugo new site my-hugo-blog
cd my-hugo-blog
```

This will create a subfolder called `my-hugo-blog`.

**b. Add a Theme**

1. Initialize Git it in your `my-hugo-blog` folder:
   
   ```powershell
   git init
   ```
   
   This is necessary for installing submodules through Git. It is better to set it up before everything else is written in this folder. This step sets up `.git` folder, which is the first step of version control. There should be an output:
   
   ```powershell
   Initialized empty Git repository in /Blog/.git/
   ```

2. Add the PaperMod theme as a submodule, but must troubleshoot CSS, which I haven't.
   
   ```powershell
   git submodule add https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
   ```

3. For some reason, the PaperMod version doesn't have CSS online rendered correctly. Switch to Ananke:
   
   ```powershell
   git submodule add https://github.com/budparr/gohugo-theme-ananke.git themes/ananke
   ```

       

**c. Create the Configuration File**

If a `hugo.toml` wasn’t created in `my-hugo-blog` folder, create one manually. Hugo changed the default configuration filename in version 0.110.0. In earlier versions, running a new site would create a file named config.toml, but now it creates hugo.toml instead. This change was made to reduce naming conflicts and improve discoverability, and if both files exist, hugo.toml takes precedence. The content you see remains essentially the same as the minimal configuration required for a new site.

1. Open Notepad:
   
   ```powershell
   notepad hugo.toml
   ```

2. Paste
   the following content (replace `<yourusername>` later with your
   Codeberg username, and we shouldn't convert underscore to hyphen now).
   
   You can choose between PaperMod and Ananke. In our example, we’ll use Ananke     since it works out of the box. (If you prefer PaperMod, be aware that additional CSS fixes might be required.
   
   This example is for PaperMod (didn't work)
   
   If you want to try PaperMod, note that you might need additional fixes for the CSS.
   
   ```toml
   baseURL = "https://thomas_router.codeberg.page/"
   languageCode = "en-us"
   title = "My Hugo Blog"
   theme = "PaperMod"
   
   [params]
     defaultTheme = "auto"
     ShowReadingTime = true
     ShowShareButtons = false
     ShowPostNavLinks = true
     ShowBreadCrumbs = true
     ShowCodeCopyButtons = true
   
   [menu]
     [[menu.main]]
       name = "Home"
       url = "/"
       weight = 1
     [[menu.main]]
       name = "Posts"
       url = "/posts/"
       weight = 2
   ```

3. And this example is for Ananke (it works):    
   
   ```toml
   baseURL = "https://thomas_router.codeberg.page/"
   languageCode = "en-us"
   title = "My Hugo Blog"
   theme = "ananke"
   canonifyURLs = true
   
   [params]
     tagline = "A Hugo site built with Ananke"
     description = "This is my Hugo blog, now powered by the Ananke theme."
   
   [menu]
     [[menu.main]]
       identifier = "home"
       name = "Home"
       url = "/"
       weight = 1
   
     [[menu.main]]
       identifier = "posts"
       name = "Posts"
       url = "/posts/"
       weight = 2
   ```

4. Save and close the file.

**d. Create Your First Blog Post**

In `my-hugo-blog` folder, Run:

```powershell
hugo new posts/my-first-post.md
```

Then, open the file at `content/posts/my-first-post.md` in Notepad and change:

`draft: true` to `draft: false`

Add your content and save.

**e. Test Your Site Locally**

Run:

```powershell
hugo server
```

Open your browser and go to [http://localhost:1313](http://localhost:1313) to view your site.

---

**4. Set Up Codeberg for Deployment**

**a. Create a Codeberg Account (if you don’t already have one)**

1. Visit [Codeberg.org](https://codeberg.org/) and click **Register**.
2. Fill in your details (choose a username, email, password) and confirm your email.

**b. Create the Deployment Repository (Must Be Named pages)**

1. Log in to Codeberg.
2. Click the **“+”** icon and select **"New Repository"**.
3. Set **Repository Name** to pages.
4. Ensure the repository is **Public** and **do not initialize** it with a README.
5. Click ***Create Repository**.

---

**5. Deploy Your Hugo Site to Codeberg Pages**

**a. Build Your Site**

In your Hugo project folder `my-hugo-blog`, run:

```powershell
hugo
```

This generates your site in the public folder.

**b. Prepare the public Folder for Deployment**

Navigate to the public folder:

```powershell
cd public
```

If you haven’t already, initialize Git and create the main branch:

```powershell
git init
git checkout -b main
```

**c. Link to the Codeberg Pages Repository**

Set the remote URL to your Codeberg pages repository:

```powershell
git remote add origin https://codeberg.org/thomas_router/pages.git
```

**Note:** Replace `<yourusername>` with your Codeberg username, `thomas_router`.  
For example, if your username is thomas_router, the live site will be served as
`https://thomas_router.codeberg.page/` . The underscore-to-hyphen conversion outdated, we should keep the underscore! This was a mistake that ChatGPT consistently made.

On the other hand, if it is for GitHub, run the following:

```powershell
git remote add origin https://github.com/thomas-router/thomas-router.github.io.git
```

We note that GitHub usernames only allow hyphens rather than underscores.

**d. Verify the Remote:**  
Check that the remote was added correctly by running:

```powershell
git remote -v
```

You should see something like:

```powershell
origin https://codeberg.org/thomas_router/pages.git (fetch)
origin https://codeberg.org/thomas_router/pages.git (push)
```

**e. Commit and Push Your Site Files**

Stage and commit your files:

```powershell
git add .
git commit -m "Deploy Hugo site"
```

Then, make sure to set up Git username and email.

```powershell
git config --global user.name "thomas_router"
git config --global user.email "thomas.router@proton.me"
```

A CodeBerg login page will open, and you need to put in your password manually.

But you can automate pushing your content without needing to manually log in every time. Here are a couple of approaches:

1. Switch to SSH Authentication:  
   Instead of using HTTPS (which may trigger a web-based login), you can configure your repository to use SSH. By setting up SSH keys and adding your public key to your Codeberg account, you can push changes automatically without interactive authentication. For example, update your remote URL to something like:
   
   `git remote set-url origin git@codeberg.org:yourusername/pages.git`
   
   This method is both secure and automation-friendly.
   
   push to Codeberg. This is a forced push. Be careful.

```powershell
git push -u origin main --force
```

**f. Verify the Deployment**

1. Visit
   your repository at https://codeberg.org/<yourusername>/pages to confirm that your files (including `index.html`) are present.
2. Your
   live site should be available at: https://thomas_router.codeberg.page/

---

**6. Troubleshooting Tips**

- **Configuration Check:**  
  Ensure that the baseURL in your config.toml exactly matches your live URL.
  For example: `baseURL = "https://thomas_router.codeberg.page/"`

- **Force a Rebuild:**  
  If changes aren’t visible, try creating or modifying a file (e.g., add a file named trigger.txt) and push the commit to force a rebuild.

- **Propagation Delay:**  
  It can take several minutes for Codeberg Pages to update. Try refreshing your browser or using an incognito window.

- **Browser Console:**  
  If the site appears empty, open the browser console (F12) to check for errors that might indicate missing assets or misconfigured links.

---

**7. Updating Your Site in the Future**

1. **Make Changes:**  
   Update your content, theme, or configuration in your Hugo project.

2. **Regenerate the Site:**
   
   Remember, this must be executed in the root Blog folder.
   
   ```powershell
   hugo
   ```

3. **Deploy Updates:** Navigate to public and push the changes. There is no need to use forced push anymore. That only matters for collaborators. When I delete a file in my local repository, `git push` will also delete them in the remote repository. And `git add .` means to add this current folder to the git list. `git commit` means to add a update label to every file.
   
   ```powershell
   cd public
   git add .
   git commit -m "Update site content"
   git push
   ```
   
   It should be noted that if the last login is yesterday or older, the credentials need to be renewed, before running `git push` as above. 
   
   ```powershell
   git config --global user.name "thomas_router"
   git config --global user.email "thomas.router@proton.me"
   ```

Your live site at [https://thomas_router.codeberg.page/](https://thomas_router.codeberg.page/) will update automatically.

In addition, if something is wrong, and `hugo` has to run again, the `public` folder should be cleared, because `hugo` does not automatically clear the old files in the `public` folder. On the other hand, when clearing the `public` folder, it is better not to touch the `.git` subfolder in `public`, so that git doesn't need to be set again. 

---

This guide covers every step—from installation to live
deployment. Save this document for your future reference, and enjoy blogging
with Hugo and Codeberg Pages! If you encounter any issues or need further
customization, feel free to revisit this guide or ask for help.
