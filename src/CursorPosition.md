---
author: malys
description: Generate and copy links to specific cursor positions and headers in markdown documents
pageDecoration.prefix: "🛠️ "
name: "Library/Malys/CursorPosition"
tags: meta/library
---
# Cursor Position Link Generator

This script provides functionality to generate and copy links to specific cursor positions and headers within markdown documents. It's particularly useful for creating precise references within a document or across multiple documents.

## Features

- **External Links**: Generate full URLs pointing to specific cursor positions or headers
- **Internal Links**: Create markdown-style internal links for use within the same document

## Usage

### External Links (Ctrl+Shift+C)
Copies a full URL to the current cursor position or header to the clipboard.
- If the cursor is on a header line: Creates a URL with the header as an anchor (e.g., `https://your-host/Page#Header Name`)
- If not on a header: Creates a URL with the cursor position (e.g., `https://your-host/Page@123`)

### Internal Links (Ctrl+Shift+L)
Copies a markdown-style internal link to the current cursor position or header.
- If on a header: Creates a link like `[Header Name@123]`
- If not on a header: Creates a link like `[Page Name@123]`
---
## Source 
```space-lua
-- [[Page#Header]] -> http(s)://host/Page#Header
-- [[Page@pos]]    -> http(s)://host/Page@pos

local function replace_space_with_percent20(s)
  local parts = {}
  for i = 1, #s do
    local c = s:sub(i, i)
    if c == " " then
      parts[#parts+1] = "%20"
    else
      parts[#parts+1] = c
    end
  end
  return table.concat(parts)
end

local function build_page_url(pageName)
  -- get direct url from js
  local BASE_URL = js.window.location.origin
  local path = replace_space_with_percent20(pageName)
  if BASE_URL:sub(-1) == "/" then
    return BASE_URL .. path
  else
    return BASE_URL .. "/" .. path
  end
end

command.define {
  name = "Cursor: Copy external link",
  key = "Ctrl-Shift-c",
  run = function()
    local currentLine = editor.getCurrentLine().text
    local pageName = editor.getCurrentPage()
    local pos = editor.getCursor()
    local headerMarks, headerName = string.match(currentLine, "^(#+) +(.+)$")
    
    local pageUrl = build_page_url(pageName)
    local out
    if headerMarks and headerName and headerName:match("%S") then
      headerName = headerName:match("^%s*(.+)")
      headerName = replace_space_with_percent20(headerName)
      out = string.format("%s#%s", pageUrl, headerName)
      -- editor.flashNotification("Copied header external link: " .. out, "info")
      editor.flashNotification("Copied header link: " .. out, "info")
    else
      out = string.format("%s@%d", pageUrl, pos)
      -- editor.flashNotification("Copied cursor external link: " .. out, "info")
      editor.flashNotification("Copied cursor link: " .. out, "info")
    end
  
    editor.copyToClipboard(out)
  end
}


command.define {
  name = "Cursor: Copy internal link",
  key = "Ctrl-Shift-l",
  run = function()
    local currentLine = editor.getCurrentLine().text
    local pageName = editor.getCurrentPage()
    local pos = editor.getCursor()
    local headerMarks, headerName = string.match(currentLine, "^(#+) +(.+)$")
    
    local out
    if headerMarks and headerName and headerName:match("%S") then
      headerName = headerName:match("^%s*(.+)")
      out = string.format("[[%s@%s]]", replace_space_with_percent20(headerName), pos)
      editor.flashNotification("Copied header internal link: " .. out, "info")
    else
      out = string.format("[[%s@%d]]", replace_space_with_percent20(pageName), pos)
      editor.flashNotification("Copied cursor internal link: " .. out, "info")
    end
  
    editor.copyToClipboard(out)
  end
}

```
