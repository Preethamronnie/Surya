# Publishing SURYA AI to GitHub from VS Code

Click-by-click. No terminal commands needed.

## Before you start

You need **Git installed** on the machine. Check: open VS Code, press
`Ctrl+Shift+G`. If it says "Install Git", get it from https://git-scm.com/download/win
and restart VS Code.

You also need to be **signed in to GitHub in VS Code**: click the account icon at
the bottom-left of the sidebar → *Sign in with GitHub*.

---

## Step 1 — Open the folder

`File → Open Folder…` → select

```
Desktop\personal\Solar project\Surya
```

Open the **Surya** folder itself, not its parent. The Explorer panel should show
`app`, `rag`, `scripts`, `static`, `data`, `docs`, `legacy`, plus `README.md`.

> **Note:** this folder lives inside OneDrive. Git and OneDrive both watch files
> for changes and can occasionally fight, producing sync-conflict copies. It works,
> but if you hit odd behaviour later, moving the project to a non-synced folder
> like `C:\dev\surya` clears it up.

## Step 2 — Check `.gitignore` is being respected

In the Explorer, `data/vectordb`, `.env`, and the PDF in `docs/` should appear
**greyed out**. That means Git will ignore them. If they look normal-coloured,
stop — `.gitignore` isn't at the folder root and you risk committing the manuals
and your API key.

## Step 3 — Initialize the repository

1. Click the **Source Control** icon in the left sidebar (the branching symbol),
   or press `Ctrl+Shift+G`.
2. Click **Initialize Repository**.

The panel now lists every file as a change, marked `U` (untracked).

## Step 4 — Make the first commit

1. Review the file list. Confirm you do **not** see `.env`, anything under
   `data/vectordb/`, or the large PDF. If you do, they aren't ignored — fix that
   before continuing.
2. Type a message in the box at the top, e.g. `Initial commit: SURYA AI RAG prototype`
3. Click **Commit** (the ✓ button).
4. If VS Code asks "There are no staged changes, stage all?" → **Yes**.

If Git complains that author identity is unknown, VS Code will prompt you for a
name and email — enter them and commit again.

## Step 5 — Publish as a private repo

1. Click **Publish Branch** (it replaces the Commit button after the first commit).
2. VS Code offers two choices in a dropdown:
   - Publish to GitHub **private** repository ← **choose this one**
   - Publish to GitHub public repository
3. Confirm the repo name (`Surya` by default — `surya-ai` reads better).
4. VS Code pushes and shows "Successfully published". Click **Open on GitHub** to
   confirm.

## Step 6 — Verify on GitHub

On the repo page, check:

- The badge next to the name says **Private**.
- `README.md` renders below the file list.
- There is no `.env` file and no `data/vectordb/` folder.
- Repo size is small (a few hundred KB). If it's hundreds of MB, a PDF or the
  index got committed — see *Undo* below.

---

## Day-to-day after this

Every subsequent change follows the same loop in the Source Control panel:

1. Edit files.
2. Type a commit message.
3. Click **Commit**.
4. Click **Sync Changes** to push.

---

## If something goes wrong

**You committed `.env` or a large file.** Deleting it in a later commit is not
enough — it stays in history. Easiest fix at this stage: delete the `.git` folder
in the Surya directory (enable *Show hidden items* in File Explorer), delete the
repo on GitHub, fix `.gitignore`, and redo from Step 3. Also **rotate your OpenAI
key** immediately if it was pushed, even to a private repo.

**Push rejected / authentication failed.** Sign out and back in: `Ctrl+Shift+P` →
*GitHub: Sign Out*, then repeat Step 5.

**"Publish Branch" doesn't appear.** You haven't committed yet. Do Step 4 first.
