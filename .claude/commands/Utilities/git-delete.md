# Git History Delete Command

⚠️ **DESTRUCTIVE OPERATION WARNING** ⚠️

This command will **permanently and irreversibly** delete the entire git history for this repository, both locally and remotely.

## What This Command Does

1. Deletes the entire local `.git` directory (all history, branches, tags, stashes)
2. Initializes a fresh git repository with zero history
3. Creates a single new commit with the current state of files
4. Force-pushes to remote, **overwriting all remote history**

## Consequences

- **All commit history permanently deleted** - cannot be recovered
- **All branches and tags lost** - only main branch will exist
- **All contributor history erased** - author information gone
- **Breaks existing clones** - collaborators cannot pull/push normally
- **Remote repository overwritten** - remote history destroyed for everyone

## Before You Proceed

**CRITICAL CHECKS:**

1. Do you have backups of important commits or branches?
2. Have you notified all collaborators?
3. Do you understand this cannot be undone?
4. Is there a less destructive alternative that meets your needs?

## Execution Instructions

Follow these steps to execute the git history deletion:

### Step 1: Confirmation

Use the AskUserQuestion tool to confirm the user wants to proceed:

**Question:** "Are you absolutely certain you want to permanently delete all git history? This operation cannot be undone and will affect all collaborators."

**Options:**
- "Yes, permanently delete all history" (proceed to Step 2)
- "No, cancel this operation" (abort immediately)

### Step 2: Get Remote Repository URL

Ask the user to provide the new repository URL where the cleaned history will be pushed:

**Question:** "What is the remote repository URL? (e.g., https://github.com/username/repo.git or git@github.com:username/repo.git)"

If the user wants to keep the existing remote, ask them to confirm they understand the remote will be force-overwritten.

### Step 3: Show Current State

Before deletion, show the user:
- Current branch
- Number of commits that will be lost
- Current remote URL
- List of all branches that will be deleted

Use these commands:
```bash
git rev-list --count HEAD
git branch -a
git remote -v
```

### Step 4: Final Confirmation

Present a final summary and ask for explicit confirmation:

**Summary to show:**
- X commits will be permanently deleted
- Y branches will be lost
- Remote repository will be force-overwritten
- Current working directory files will be preserved

**Final question:** "Type 'DELETE HISTORY' to confirm and proceed, or anything else to cancel."

### Step 5: Execute Deletion

Only if user provided exact confirmation, execute these commands sequentially:

```bash
# Remove all git history
rm -rf .git

# Initialize fresh repository
git init

# Stage all current files
git add .

# Create initial commit
git commit -m "Initial clean commit"

# Rename branch to main
git branch -M main

# Add remote (use URL from Step 2)
git remote add origin <repository-url>

# Force push to remote (overwrites remote history)
git push -u origin main --force
```

### Step 6: Verification and Summary

After execution, verify success:

```bash
# Verify clean state
git log --oneline
git status
git remote -v
```

Show the user:
- ✅ Git history successfully deleted
- ✅ Fresh repository initialized with 1 commit
- ✅ Remote repository overwritten
- ⚠️ All collaborators must re-clone the repository

### Step 7: Next Steps for Collaborators

Inform the user to notify all collaborators to:

```bash
# Delete their local clone
cd ..
rm -rf <repo-directory>

# Clone fresh copy
git clone <repository-url>
```

## Error Handling

- If any command fails, stop immediately and report the error
- Do not proceed to force push if earlier steps fail
- Preserve the .git directory if initialization fails

## Safety Notes

- This command does NOT delete working directory files
- Only git metadata and history are removed
- Files in .gitignore remain untracked
- Current file state becomes the "initial commit"

Execute these steps carefully and ensure the user fully understands the consequences at each confirmation point.
