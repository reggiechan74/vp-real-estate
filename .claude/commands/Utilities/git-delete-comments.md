---
description: Replace entire git commit messages with generic text using commit IDs
argument-hint: <commit-id> [commit-id2 commit-id3 ...]
allowed-tools: Read, Bash, AskUserQuestion
---

You are a git security specialist. Your task is to replace sensitive commit messages with generic text using `git filter-repo`.

## Input

The user will provide one or more **commit IDs** (short or full SHA) to redact.

**Arguments provided**: {{args}}

## ⚠️ IMPORTANT NOTES ⚠️

**This command:**
- ✅ Replaces the entire commit **message** with generic text
- ✅ Preserves all **file changes** in the commit
- ✅ Keeps the commit in history (does not delete the commit)

**This command does NOT:**
- ❌ Remove files from repository history
- ❌ Delete commits entirely
- ❌ Redact specific words/phrases (it replaces the whole message)

**For removing files from history**, use a different tool like `git filter-repo --path` or BFG Repo-Cleaner.

## Execution Process

### Step 1: Parse Arguments

Extract commit IDs from arguments. Examples:
- Single commit: `abc123`
- Multiple commits: `abc123 def456 ghi789`

If no arguments provided, ask the user:
- "What commit ID(s) should have their messages redacted?"

### Step 2: Validate Prerequisites

Check that `git-filter-repo` is installed:

```bash
git filter-repo --version
```

If not installed, install it:

```bash
pip3 install git-filter-repo
```

### Step 3: Validate Commit IDs

For each commit ID provided:

```bash
# Verify the commit exists
git show <commit-id> --format="%H|||%s|||%b" --stat
```

Show the user:
- Full commit SHA
- Current commit message (subject + body)
- Files changed in the commit
- Number of lines changed

If any commit ID is invalid, stop and report the error.

### Step 4: Check Repository State

```bash
# Show current remote
git remote -v

# Count total commits
git rev-list --count --all

# Check for uncommitted changes
git status --short
```

**Show the user:**
- Current remote URL
- Total commits in repository
- Warning if uncommitted changes exist (must be committed or stashed first)

### Step 5: Preview and Confirmation

For each commit to be redacted, show:

```
Commit: abc123def456...
Current message:
  docs: Add Dennis's institutional career background and credentials

  Enhanced Dennis agent with detailed career history:
  - President, Standard Life Realty Advisors (2003-2006): $5.5B AUM
  - Top quartile fund performance...
  [etc]

New message will be:
  docs: Update documentation

  Updated documentation with additional context.

Files affected: 2 files changed, 44 insertions(+), 2 deletions(-)
```

Use AskUserQuestion with:

**Question:** "Proceed with redacting these commit messages? This will rewrite git history."
- **Options:**
  - "Yes, replace commit messages with generic text"
  - "No, cancel operation"

### Step 6: Create Backup Tag

```bash
git tag -a backup-before-redaction-$(date +%Y%m%d-%H%M%S) -m "Backup before commit message redaction"
```

Show the backup tag name to the user for reference.

### Step 7: Execute Redaction

Build a Python script for git filter-repo that replaces specific commit messages:

```bash
git filter-repo --force --commit-callback '
# Replace commit messages for specified commits
COMMITS_TO_REDACT = {
    b"<full-sha-1>": b"""docs: Update documentation

Updated documentation with additional context.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
""",
    b"<full-sha-2>": b"""refactor: Refactor code structure

Refactored code structure for better organization.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
""",
}

if commit.original_id in COMMITS_TO_REDACT:
    commit.message = COMMITS_TO_REDACT[commit.original_id]
'
```

**Important implementation notes:**
- Use the **full 40-character SHA** for each commit
- Use byte strings (prefix with `b`)
- Create generic messages based on the original commit type:
  - `docs:` → "Update documentation"
  - `feat:` → "Add new feature"
  - `refactor:` → "Refactor code structure"
  - `fix:` → "Fix issue"
  - Default → "Update codebase"
- The `--force` flag is required if repo was filtered before
- git filter-repo will remove the `origin` remote (re-add it after)

### Step 8: Re-add Remote and Verify

```bash
# Re-add the origin remote
git remote add origin <original-remote-url>

# Verify redaction was successful
git log --oneline | head -20

# Show the redacted commits
git show <new-commit-id> --format="%H %s%n%b" --stat
```

**Verification criteria:**
- ✅ Commit messages are now generic
- ✅ File changes are preserved (same number of files/lines changed)
- ✅ Repository is functional
- ✅ Total commit count unchanged

If verification fails, restore from backup and report error.

### Step 9: Next Steps Guidance

**DO NOT automatically force push.** Instead, inform the user:

```
✅ Commit message redaction completed successfully

📊 Summary:
- Commits redacted: <count>
- Total commits processed: <total>
- File changes: Preserved
- Backup tag: backup-before-redaction-XXXXXXXX

⚠️ CRITICAL NEXT STEPS:

1. Review the changes:
   git log --oneline | head -20
   git show <new-commit-id>

2. If satisfied, force push to remote:
   git push origin --force --all
   git push origin --force --tags

3. If you have collaborators, notify them to:
   - Delete their local clones
   - Clone fresh copies
   - DO NOT attempt to pull or merge

4. To abort and restore original history:
   git reset --hard backup-before-redaction-XXXXXXXX
   git push origin --force --all
```

## Error Handling

### If git-filter-repo is not installed:
```bash
pip3 install git-filter-repo
```

### If commit ID doesn't exist:
```
Error: Commit 'abc123' not found in repository
Did you mean one of these?
  - abc1234 (docs: Add feature)
  - abc5678 (fix: Bug fix)
```

### If uncommitted changes exist:
```
Error: You have uncommitted changes. Please commit or stash them first:
  git stash
or
  git add . && git commit -m "WIP"
```

### If filter-repo fails:
- Show exact error message
- Check if `--force` flag is needed
- Suggest restoring from backup tag

## Usage Examples

**Single commit:**
```bash
/git-delete-comments abc123
```

**Multiple commits:**
```bash
/git-delete-comments abc123 def456 ghi789
```

**With full SHA:**
```bash
/git-delete-comments 9c9d6452ea1ece6b2ba4531003b11c2a0a37f645
```

## Generic Message Templates

Based on the original commit prefix, use these templates:

- **`docs:`** → "Update documentation" + "Updated documentation with additional context."
- **`feat:`** → "Add new feature" + "Added new feature implementation."
- **`refactor:`** → "Refactor code structure" + "Refactored code structure for better organization."
- **`fix:`** → "Fix issue" + "Fixed issue in codebase."
- **`chore:`** → "Update build configuration" + "Updated build configuration and dependencies."
- **`test:`** → "Update tests" + "Updated test suite."
- **`style:`** → "Update code formatting" + "Updated code formatting and style."
- **Default** → "Update codebase" + "Updated codebase with changes."

Always append the Claude Code attribution:
```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Success Criteria

- ✅ git-filter-repo successfully rewrites repository history
- ✅ Commit messages replaced with generic text
- ✅ File changes preserved in all commits
- ✅ Repository remains functional
- ✅ Backup tag created for safety
- ✅ Total commit count unchanged
- ✅ User informed about force push requirements
