---
author: malys
description: Implement Git commands (log, diff, revert)
name: "Library/Malys/GitHistory"
tags: meta/library
---
---
# Git History Module

## 🎯 Description

This module adds full **Git integration** into SilverBullet / Space-Lua.

It provides:

* 🕘 **Commit history browser** for the current `.md` file
* 🧾 **View file contents** at any commit
* 🔍 **Compare (diff)** between two commits, rendered in Markdown
* ♻️ **Restore** any commit into the active editor buffer
* 📌 **View Git status** as clean, emoji-enhanced Markdown
* 📄 **Virtual pages** to navigate Git history like normal documents

> **warning** Warning
> Depends on:
>  `git` CLI
>  `utilities.debug` helper

---

## ⚙️ How It Works

### ✔️ Virtual Pages

The module registers custom pages:

| Virtual Page Pattern | Purpose                                    |
| -------------------- | ------------------------------------------ |
| `git:<path_hash>`    | Displays file content at a specific commit |
| `diff:<ref1>,<ref2>` | Shows a diff between two commits           |
| `git status`         | Shows Git status in Markdown               |

The user can navigate to these pages just like regular documents.

---

### ✔️ Commands

The module adds SilverBullet commands:

| Command          | Action                             |
| ---------------- | ---------------------------------- |
| **Git: History** | Pick a commit and view its content |
| **Git: Diff**    | Pick 2 commits → view diff         |
| **Git: Status**  | Display `git status`               |
| **Git: Restore** | Load an old commit into the editor |

Everything is interactive using `editor.filterBox()` and `editor.navigate()`.

---

### ✔️ Markdown Rendering

The module converts raw Git output to readable Markdown:

* 🟢 additions
* 🔴 deletions
* 🟦 context lines
* 🆕 untracked files
* 🟡 unstaged modifications
* 🟠 staged modifications
* 🔁 renamed files

---

# 🧩 Code

```space-lua
-- ###########################################################################
-- ## Git History Module (complete, restored)
-- ## Depends on: Utilities.md (utilities.debug), and environment helpers:
-- ##   string.trim, string.split, string.startsWith, shell.run, editor.*, virtualPage.*, command.*
-- ###########################################################################

-- ===========================================================================
-- == Configuration
-- ===========================================================================
local LOG_ENABLE = false

local function log(...)
  if LOG_ENABLE and utilities and utilities.debug then
     -- utilities.debug(table.concat({...}, " "))
  end
end

local current_panel_id = "rhs"
local is_panel_visible = false

-- ===========================================================================
-- == Shell Helpers
-- ===========================================================================
---
-- Executes a shell command and returns its stdout.
-- Throws an error on non-zero exit code.
-- @param cmd string
-- @param args table
-- @return string stdout
local function run_shell_command(cmd, args)
  log("Running command:", cmd, table.concat(args or {}, " "))
  local result = shell.run(cmd, args)
  if not result then
    error("shell.run returned nil for: " .. cmd)
  end
  if result.code ~= 0 then
    error("Command failed: " .. cmd .. " " .. table.concat(args or {}, " ") .. "\n" .. (result.stderr or ""))
  end
  return result.stdout or ""
end

-- ===========================================================================
-- == Git Status & Properties
-- ===========================================================================
---
-- Returns true if current working dir is a git repository.
local function is_git_repo()
  local result = run_shell_command("git", { "rev-parse", "--is-inside-work-tree" })
  return string.trim(result) == "true"
end

---
-- Returns true if a file is tracked by git.
-- @param file_path string
local function is_git_tracked(file_path)
  local stdout = run_shell_command("git", { "status", "--porcelain", "--", file_path })
  return not string.startsWith(string.trim(stdout), "??")
end

---
-- Returns true if a file has uncommitted changes.
-- @param file_path string
local function has_uncommitted_changes(file_path)
  local stdout = run_shell_command("git", { "status", "--porcelain", "--", file_path })
  return string.trim(stdout) ~= ""
end

-- ===========================================================================
-- == Git Log & File Access
-- ===========================================================================
---
-- Format git unix timestamp to human string.
-- @param ts number (seconds)
local function format_git_timestamp(ts)
  return os.date("%Y-%m-%d at %H:%M:%S", ts)
end

---
-- Get the newest commit hash for a file.
-- @param file_path string
local function get_newest_version(file_path)
  local stdout = run_shell_command("git", { "log", "-1", "--format=%h", "--", file_path })
  return string.trim(stdout)
end

---
-- Get the contents of a file at a specific commit.
-- @param file_path string (path relative to repo)
-- @param hash string commit hash
local function get_file_contents(file_path, hash)
  log("get_file_contents:", file_path, "at", hash)
  return run_shell_command("git", { "show", hash .. ":" .. file_path })
end

---
-- Get commit history for a given file.
-- Returns a table of entries suitable for editor.filterBox.
-- Each entry: { name, description, ref, type, prefix, timestamp }
-- @param file_path string
local function get_history(file_path)
  log("get_history:", file_path)
  local stdout = run_shell_command("git", { "log", "--format=%h %ct %s", "--", file_path })
  stdout = string.trim(stdout)
  if stdout == "" then
    return {}
  end

  local lines = string.split(stdout, "\n")
  local commits = {}

  for _, line in ipairs(lines) do
    if line and line ~= "" then
      local parts = string.split(line, " ", 3)
      if #parts == 3 then
        local hash = parts[1]
        local ts = tonumber(parts[2]) or 0
        local msg = parts[3] or ""
        table.insert(commits, {
          name        = hash,
          description = msg .. " - " .. format_git_timestamp(ts),
          ref         = string.gsub(file_path, "%.md$", "") .. "_" .. hash,
          type        = "commits",
          prefix      = "⚡",
          timestamp   = ts
        })
      end
    end
  end

  table.sort(commits, function(a, b)
    return (a.timestamp or 0) > (b.timestamp or 0)
  end)

  return commits
end

-- ===========================================================================
-- == Git Status Renderer
-- ===========================================================================
---
---
-- Get and render git status.
local function get_git_status()
  local raw = run_shell_command("git", { "status", "--porcelain" })
  return gitstatus_render(string.trim(raw))
end

-- ===========================================================================
-- == Diff Tools
-- ===========================================================================

---
-- Compute diff between two commits for a given file path.
-- @param hash_old string
-- @param hash_new string
-- @param file_path string (path to file in repo)
local function get_diff_between_commits(hash_old, hash_new, file_path)
  log("get_diff_between_commits:", hash_old, hash_new, file_path)
  local raw = run_shell_command("git", { "diff", "--no-color", hash_old, hash_new, "--", file_path })
  raw = string.trim(raw)
  if raw == "" then
    return "### 🟢 No Differences Found"
  end
  local path=string.gsub(file_path,".md","")
  local old="[[git:"..path.."_"..hash_old.."|".. hash_old .."]]"
  local new="[[git:"..path.."_"..hash_new.."|".. hash_new .."]]"
  return  "### 🔍[["..path.. "]] : diff between " .. old .. " and " .. new .."\n" .."${gitdiff_render(\"".. encoding.base64Encode(raw).."\")}"
end

-- ===========================================================================
-- == Helpers for virtual refs
-- ===========================================================================
---
-- Parse a virtual ref "path_hash" and fetch content.
-- returns { path=..., hash=..., content=... }
local function get_content(ref)
  local data = string.split(ref, "_")
  if #data > 1 then
    local path = data[1]
    local hash = data[2]
    local ok, content = pcall(get_file_contents, path .. ".md", hash)
    if not ok then
      log("get_content error for", ref, content)
      return { path = path, hash = hash, content = nil }
    end
    return { path = path, hash = hash, content = content }
  end
  return { path = nil, hash = nil, content = nil }
end

-- ===========================================================================
-- == Virtual Pages
-- ===========================================================================
virtualPage.define {
  pattern = "git:(.+)",
  run = function(ref)
    local result = get_content(ref).content
    if result == nil then
      editor.flashNotification("Path " .. ref .. " corrupted", "error")
    end
    return result
  end
}

virtualPage.define {
  pattern = "git status",
  run = function()
    return get_git_status()
  end
}

virtualPage.define {
  pattern = "diff:(.+)",
  run = function(ref)
    local data = string.split(ref, ",")
    if #data > 1 then
      local from = get_content(data[1])
      local to = get_content(data[2])
      if not from or not to or not from.hash or not to.hash or not from.path then
        editor.flashNotification("Path " .. ref .. " corrupted", "error")
        return nil
      end
      return get_diff_between_commits(from.hash, to.hash, from.path .. ".md")
    end
    editor.flashNotification("Path " .. ref .. " corrupted", "error")
    return nil
  end
}

-- ===========================================================================
-- == Commands
-- ===========================================================================
---
-- Browse commit history and open a commit.
command.define {
  name = "Git: History",
  run = function()
    local file_path = editor.getCurrentPage() .. ".md"
    local history = get_history(file_path)
    if not history or #history == 0 then
      editor.flashNotification("No git history for " .. file_path, "info")
      return
    end
    local selected = editor.filterBox("📜 Git History", history, "🔍 Select a commit", "Type to search...")
    if selected and selected.ref then
      editor.navigate("git:" .. selected.ref)
    end
  end
}

---
-- Select two commits and show their diff.
command.define {
  name = "Git: Diff",
  run = function()
    local file_path = editor.getCurrentPage() .. ".md"
    local history = get_history(file_path)
    if not history or #history == 0 then
      editor.flashNotification("No git history for " .. file_path, "info")
      return
    end
    local from = editor.filterBox("📜 Git History", history, "🔍 Select 1st commit")
    local to = editor.filterBox("📜 Git History", history, "🔍 Select 2nd commit")
    if from and to and from.ref and to.ref then
      editor.navigate("diff:" .. from.ref .. "," .. to.ref)
    end
  end
}

---
-- Restore a chosen commit to the current buffer.
command.define {
  name = "Git: Restore",
  run = function()
    local file_path = editor.getCurrentPage() .. ".md"
    local history = get_history(file_path)
    if not history or #history == 0 then
      editor.flashNotification("No git history for " .. file_path, "info")
      return
    end
    local selected = editor.filterBox("♻️ Restore", history, "Select commit to restore")
    if not selected or not selected.ref then
      return
    end
    local data = get_content(selected.ref)
    if not data or not data.content then
      editor.flashNotification("Could not restore this commit", "error")
      return
    end
    editor.setText(data.content)
    editor.flashNotification("Commit restored: " .. (data.hash or "unknown"), "success")
  end
}

---
-- Show git status in a virtual page.
command.define {
  name = "Git: Status",
  run = function()
    editor.navigate("git status")
  end
}

```

## Renderers

```space-lua
-- Render `git status --porcelain` into readable Markdown.
-- Uses emojis to indicate status.
function gitstatus_render(raw)
  if not raw or raw == "" then
    return "### 🟢 Clean Working Tree\nNo changes."
  end

  local md = { "### 📌 Git Status\n" }

  for line in raw:gmatch("[^\r\n]+") do
    local code = line:sub(1, 2)
    local path = string.trim(line:sub(3) or "")

    if code == "??" then
      table.insert(md, "🆕 Untracked: " .. path)
    elseif code == " M" then
      table.insert(md, "🟡 Modified (unstaged): " .. path)
    elseif code == "M " then
      table.insert(md, "🟠 Modified (staged): " .. path)
    elseif code == " D" then
      table.insert(md, "🔴 Deleted (unstaged): " .. path)
    elseif code == "D " then
      table.insert(md, "🛑 Deleted (staged): " .. path)
    elseif code == "A " or code == " A" then
      table.insert(md, "🟢 Added: " .. path)
    elseif code == "R " or code == " R" then
      table.insert(md, "🔁 Renamed: " .. path)
    elseif code == "C " or code == " C" then
      table.insert(md, "📄 Copied: " .. path)
    else
      table.insert(md, "🟦 " .. code .. " " .. path)
    end
  end

  return table.concat(md, "\n")
end


-- Render raw git diff.
function gitdiff_render(base64Text)
  local diffText= encoding.utf8Decode(encoding.base64Decode(base64Text))
  local lines = string.split(diffText, "\n")  
  local html = '<pre class="git-diff">'  
    
  for _, line in ipairs(lines) do  
    if string.startsWith(line, "---") or string.startsWith(line, "+++") then  
      html = html .. '<div class="diff-header">' .. line .. '</div>'  
    elseif string.startsWith(line, "@@") then  
      html = html .. '<div class="diff-hunk">' .. line .. '</div>'  
    elseif string.startsWith(line, "-") then  
      html = html .. '<div class="diff-delete">' .. line .. '</div>'  
    elseif string.startsWith(line, "+") then  
      html = html .. '<div class="diff-add">' .. line .. '</div>'  
    else  
      html = html .. '<div class="diff-context">' .. line .. '</div>'  
    end  
  end  
  html = html..'</pre>'  
  return widget.htmlBlock(html)
end

```
## CSS
```space-style
.git-diff {  
  font-family: monospace;  
  margin: 0;  
}  
.diff-header { color: #888; font-weight: bold; }  
.diff-hunk { color: #0066cc; }  
.diff-delete { background-color: #ffdddd; color: #cc0000; }  
.diff-add { background-color: #ddffdd; color: #00cc00; }  
.diff-context { color: inherit; }

```
