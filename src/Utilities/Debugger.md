---
author: malys
description: Tooling to debug (linter, postion, beautify)
name: "Library/Malys/Debugger"
tags: meta/library
---
# SpaceLua Debugger - Enhance Your Development Workflow

## Description: 

This SpaceLua script provides a set of tools designed to aid in the development and debugging of Lua code directly within the Silverbullet environment. It helps you identify errors, improve code quality, and maintain consistent formatting.  

## Features

*   **Lua Linting:**  Integrates with `luacheck` to automatically analyze your code for potential errors, stylistic issues, and adherence to best practices. Issues are clearly displayed within Silverbullet.
*   **Code Formatting (Beautification):** Utilizes `lua-format` to automatically format your Lua code, ensuring consistent indentation, spacing, and overall readability.  The formatted code is conveniently copied to your clipboard.
*   **Position Highlighting:** Allows you to quickly locate and visually inspect code at a specific character position.  This is useful when dealing with error messages that point to a particular location within your Lua files.
*   **Easy Access with Slash Commands:**  The script offers three slash commands for rapid execution of key features:
    *   `/debugger:check` - Runs Lua linting on the current code block.
    *   `/debugger:beautify` - Formats the current code block and copies it to the clipboard.
    *   `/debugger:position` - Prompts you for a character position and highlights the corresponding code in a panel.
*   **Dedicated Lint Panel:**  A toggleable panel on the right-hand side of the editor continuously displays linting information, providing real-time feedback as you write code. This panel automatically updates when you save your page.

## How to Use:

1.  **Installation:** The script automatically attempts to install required dependencies (`Utilities.md` and `Luacheck.md`) from the Silverbullet library repository. You'll see a notification if installation is successful or if there are any errors.
2.  **Code Block Designation:**  Place the Lua code you want to debug within a Silverbullet code block specifically labelled with the tag `space-lua`.  The script will automatically identify and process this code block.
3.  **Executing Commands:**  Type the corresponding slash command into the Silverbullet editor to trigger:
    *   **Linting:**  Type `/debugger:check` and press Enter. The results will be displayed in the editor.
    *   **Formatting:** Type `/debugger:beautify` and press Enter. The formatted code will be inserted into the editor and copied to your clipboard.
    *   **Position Highlighting:** Type `/debugger:position` and press Enter. You will be prompted to enter a character position.  Enter the position and press Enter again to see the code highlighted in a panel.
4.  **Using the Lint Panel:**  Run the command `Debugger: Toggle Lint Panel` to show a panel with linting errors.  The panel automatically reloads when the page is saved.

## Disclaimer & Contributions

This code is provided **as-is**, **without any kind of support or warranty**.  
I do **not** provide user support, bug-fixing on demand, or feature development.

If you detect a bug, please **actively participate in debugging it** (analysis, proposed fix, or pull request) **before reporting it**. Bug reports without investigation may be ignored.

🚫 **No new features will be added.**  
✅ **All types of contributions are welcome**, including bug fixes, refactoring, documentation improvements, and optimizations.

By using or contributing to this project, you acknowledge and accept these conditions.

## Code
```space-lua
mls=mls or {}
if mls == nil or (mls ~= nil and mls.debug == nil) or (mls ~= nil and mls.luacheck == nil) then
	library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities.md")
	library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities/Luacheck.md")
	editor.flashNotification("'Depencies' has been installed", "Info")
end

 function mls.removeFirstLines(text, n)
  local lines = string.split(text, "\n")
  if #lines <= n then
    return ""
  end
  return table.concat(lines, "\n", n + 1)
end

 function mls.formatLua(text)
  local prettier = js.import("https://cdn.jsdelivr.net/npm/lua-format/+esm")
  local result= prettier.Beautify(text,{
    RenameVariables= false,
    RenameGlobals= false,
    SolveMath= false,
    Indentation= '\t'
  })
  local result=mls.removeFirstLines(result,6) 
   js.window.navigator.clipboard.writeText(result)
  return result
end

function mls.defaultCheck(debugCode)
  return mls.luacheck(debugCode, {allowDefined=true, unused=true, globals = {"_CTX", "mls","LOG_ENABLE","asset","clientStore","codeWidget","command","config","datastore","editor","encoding","event","global","http","index","js","jsonschema","language","lua","markdown","math","mq","net","os","service","shell","slashCommand","space","spacelua","string","sync","system","table","template","yaml","asset","clientStore","codeWidget","command","config","datastore","editor","encoding","event","global","http","index","js","jsonschema","language","lua","markdown","math","mq","net","os","service","shell","slashCommand","space","spacelua","string","sync","system","table","template","yaml"} })
end 

function mls.checkAction(debugCode)
  local result = mls.defaultCheck(debugCode)
  if not result then
    return widget.htmlBlock("<div style='color:#eee'>Luacheck failed to run</div>")
  end

  local html = {}

  table.insert(html, [[
    <div style="
      border: 1px solid #333;
      padding: 12px;
      margin: 6px 0;
      border-radius: 8px;
      background-color: #1e1e1e;
      color: #e0e0e0;
      font-family: system-ui, -apple-system, sans-serif;
    ">
  ]])

  -- Status
  if result.success then
    table.insert(html, [[
      <div style="color: #81c784; font-weight: 600; margin-bottom: 6px;">
        ✅ Luacheck passed
      </div>
    ]])
  else
    table.insert(html, [[
      <div style="color: #ef5350; font-weight: 600; margin-bottom: 6px;">
        ❌ Luacheck found issues
      </div>
    ]])
  end

  -- Summary
  local issueCount = result.issues and #result.issues or 0
  table.insert(html, string.format(
    "<div style='margin-bottom: 10px; color: #9e9e9e;'>Issues: %d</div>",
    issueCount
  ))

  -- Issues list
  if issueCount > 0 then
    table.insert(html, [[
      <ul style="
        padding-left: 18px;
        margin: 0 0 12px 0;
        font-family: monospace;
        font-size: 13px;
        line-height: 1.4;
      ">
    ]])

    for _, issue in ipairs(result.issues) do
      table.insert(html, string.format(
        "<li style='margin-bottom: 4px;'>"
        .. "<span style='color:#64b5f6; font-weight:600;'>L%d:%d</span>"
        .. "<span style='color:#e0e0e0;'> — %s</span>"
        .. "</li>",
        issue.line,
        issue.column,
        issue.message
      ))
    end

    table.insert(html, "</ul>")
  end

  -- Raw output (collapsible)
  if result.output and result.output ~= "" then
  table.insert(html, '<details><summary style="cursor:pointer;color:#bdbdbd;margin-bottom:6px;">Raw luacheck output</summary><pre style="background:#111;padding:10px;border-radius:6px;overflow-x:auto;font-family:monospace;font-size:12px;line-height:1.4;color:#cfcfcf;white-space:pre-wrap;border:1px solid #2a2a2a;">' .. result.output .. '</pre></details>')
  end

  table.insert(html, "</div>")

  return widget.htmlBlock(table.concat(html))
end

 function mls.positionAction(debugCode, position)  
  -- Position is a character position (number)  
  local pos = tonumber(position) or 0  
    
  -- Extract lines around position  
  local lines = string.split(debugCode, "\n")  
  local currentPos = 0  
  local targetLineIndex = -1  
  local targetColInLine = 0  
    
  -- Find which line contains the position  
  for i = 1, #lines do  
    local lineLength = string.len(lines[i]) + (i < #lines and 1 or 0) -- +1 for newline except last line  
    if pos >= currentPos and pos < currentPos + lineLength then  
      targetLineIndex = i - 1 -- 0-based index  
      targetColInLine = pos - currentPos  
      break  
    end  
    currentPos = currentPos + lineLength  
  end  
    
  local snippet = ""  
  local lineNum = 0  
  local colNum = 0  
    
  if targetLineIndex >= 0 then  
    -- Convert to 1-based for display  
    lineNum = targetLineIndex + 1  
    colNum = targetColInLine + 1  
      
    -- Always get line before and after if they exist  
    local startLine = math.max(1, targetLineIndex)  
    local endLine = math.min(#lines, targetLineIndex + 2)  
      
    -- If we have a line before, include it  
    if targetLineIndex > 0 then  
      startLine = targetLineIndex  
    end  
      
    local selectedLines = {}  
    for i = startLine, endLine do  
      table.insert(selectedLines, lines[i])  
    end  
      
    snippet = table.concat(selectedLines, "\n")  
      
    -- Find and highlight the word at position  
    local lineWithPos = lines[targetLineIndex + 1]  
    local wordStart = targetColInLine  
    local wordEnd = targetColInLine  
      
    -- Find word start (go back until non-word character)  
    while wordStart > 1 do  
      local char = string.sub(lineWithPos, wordStart, wordStart)  
      if not string.match(char, "[%w_]") then  
        wordStart = wordStart + 1  
        break  
      end  
      wordStart = wordStart - 1  
    end  
      
    -- Find word end (go forward until non-word character)  
    while wordEnd <= string.len(lineWithPos) do  
      local char = string.sub(lineWithPos, wordEnd, wordEnd)  
      if not string.match(char, "[%w_]") then  
        wordEnd = wordEnd - 1  
        break  
      end  
      wordEnd = wordEnd + 1  
    end  
      
    -- Extract the word  
    local word = string.sub(lineWithPos, wordStart, wordEnd)  
      
    -- Calculate position in snippet  
    local posInSnippet = targetColInLine  
    if targetLineIndex > 0 then  
      -- Add previous line length + newline  
      posInSnippet = posInSnippet + string.len(lines[targetLineIndex]) + 1  
    end  
      
    -- Insert highlight marker  
    local beforeWord = string.sub(snippet, 1, posInSnippet  )  
    local afterWord = string.sub(snippet, posInSnippet + (targetColInLine - wordStart) + 2)  
            
    local HIGHLIGHT_STYLE =
      'background-color:#fedaff;'
      .. 'color:#ffcc66;'
      .. 'font-weight:600;'
      .. 'padding:1px 3px;'
      .. 'border-radius:3px;'
    
    snippet = beforeWord
      .. '<span style="' .. HIGHLIGHT_STYLE .. '">' .. word .. '</span>'
      .. afterWord
  end  
    
  -- Return HTML widget with highlighted code and position conversion  
  return widget.htmlBlock([[  
    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px 0; border-radius: 5px; background-color: #1e1e1e;">  
      <strong>Code at position ]] .. position .. [[ (Line ]] .. lineNum .. [[, Character ]] .. colNum .. [[):</strong>  
      <pre style="background: #1e1e1e; padding: 10px; border-radius: 3px; overflow-x: auto; font-family: monospace; line-height: 1.4;">]] .. snippet .. [[</pre>  
    </div>  
  ]])  
end

 function mls.beautifyAction(debugCode)
  -- Format code using prettier
  local formattedText = mls.formatLua(debugCode)
  return formattedText
end

function mls.getDebugCode(page)
  local target = page  or editor.getCurrentPage()
  local debugCode = mls.getCodeBlock(target,"space-lua")
  if debugCode =="Not found" then
    editor.flashNotification("Could not find debug code block with label 'debug'", "error")
    return "Error: Could not find debug code block"
  end
  return debugCode
end

function mls.debugger(action, parameters)
  local debugCode=mls.getDebugCode()
  if debugCode ~= "Not found" then
    if action == "position" then
      local position = parameters
      return mls.positionAction(debugCode, position)
    elseif action == "beautify" then
      return mls.beautifyAction(debugCode)
    elseif action == "check" then
      return mls.checkAction(debugCode)
    else
      return "Error: Unsupported action '" .. action .. "'"
    end
    return "Error: "..debugCode
  end 
end
-- slash command
slashcommand.define {
  name = "debugger:check",
  description="lua linter for space-lua",
  run = function()
    editor.insertAtCursor( '${mls.debugger("check")}\n', false, true)
  end
}
slashcommand.define {
  name = "debugger:beautify",
  description="format space-lua code",
  run = function()
    editor.insertAtCursor( '${mls.debugger("beautify")}\n', false, true)
  end
}
slashcommand.define {
  name = "debugger:position",
  description="highlight character to specific position",
  run = function()
    local result = editor.prompt("Enter position:")
    editor.insertAtCursor( '${mls.debugger("position",'..result..')}\n', false, true)
  end
}
-- Lint panel
local is_panel_visible = false
local current_panel_id = "rhs"

-- Function to render code with lint info
local function render_code_lint_panel(force)
    -- Get editor text
    local code = mls.getDebugCode()
    if code ~= "Not found" and code ~=nil then  
      local lines = string.split(code,"\n")
      local lint_result = mls.defaultCheck(code)
      -- Parse lint messages
      local messages = {} -- key: line number, value: array of messages
      if lint_result.success == false and lint_result.issues then
          for _, issue in ipairs(lint_result.issues) do
              messages[issue.line] = messages[issue.line] or {}
              table.insert(messages[issue.line], issue.message)
          end
      end
  
      -- Build HTML with line numbers and lint comments
      local html_lines = {}
      for i, line in ipairs(lines) do
          -- Add lint messages above the line
          if messages[i] then
              for _, msg in ipairs(messages[i]) do
                  table.insert(html_lines, string.format('<span style="color:#ff5555">--🪲 %s</span>', msg))
              end
          end
          -- Add code line with line number
          table.insert(html_lines, string.format('<span style="color:#ccc"><span style="color:#888">%3d │ </span>%s</span>', i, line:gsub(" ", "&nbsp;")))
      end
  
      local panel_html = string.format('<pre style="font-family: monospace; font-size: 14px; color: #ccc;  padding: 12px;margin: 0; overflow-x: auto; line-height: 1.4em;">%s</pre>', table.concat(html_lines, "\n"))
  
      if not is_panel_visible or force then
          editor.showPanel(current_panel_id, 2, panel_html, "")
          is_panel_visible = true
      else
          editor.hidePanel(current_panel_id)
          is_panel_visible = false
      end
   else
      editor.flashNotification("Code not found","error")
   end      
end

-- Define the command
command.define({
    name = "Debugger: Toggle Lint Panel",
    description = "Show code with lint info on the right",
    run = function()
        render_code_lint_panel(false)
    end
})

-- Optional: Update panel on save
event.listen({
    name = "editor:pageSaved",
    run = function()
        if is_panel_visible then
            render_code_lint_panel(true)
        end
    end
})

```


## Changelog

* 2026-01-04 feat: implement check, beautify and position 

## Community

[Silverbullet forum](https://community.silverbullet.md/t/mindmap-with-markmap-js/1556/7)