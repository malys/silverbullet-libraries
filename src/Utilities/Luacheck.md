---
author: malys
description: Lua linter.
name: "Library/Malys/Luacheck"
tags: meta/library
---
## Lua linter

This library provides a wrapper for [luacheck](https://luacheck.readthedocs.io/en/stable/#), a LUA code linter .

## Features

* `mls.luacheck = function(code, options)`: lint LUA code
  
## Disclaimer & Contributions

This code is provided **as-is**, **without any kind of support or warranty**.  
I do **not** provide user support, bug-fixing on demand, or feature development.

If you detect a bug, please **actively participate in debugging it** (analysis, proposed fix, or pull request) **before reporting it**. Bug reports without investigation may be ignored.

🚫 **No new features will be added.**  
✅ **All types of contributions are welcome**, including bug fixes, refactoring, documentation improvements, and optimizations.

By using or contributing to this project, you acknowledge and accept these conditions.

## Prerequisites

### Luacheck installation

* Add to `CONTAINER_BOOT` page

```bash
apk add luacheck 
```
* Reload Silverbullet container

## Code
```space-lua
mls = mls or {}

if mls == nil or (mls ~= nil and mls.debug == nil) then
	library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities.md")
	editor.flashNotification("'Depencies' has been installed", "Info")
end

-- Template to run luacheck on Lua code and format results
mls.luacheck = function(code, options)
  options = options or {}

  -- Create temporary file
  local tempFile = "temp/luacheck_" .. math.random(10000, 99999) .. ".lua"

  local meta = space.writeFile(tempFile, code)
  if not meta then
    return {
      success = false,
      output = "Failed to write temporary file",
      issues = {}
    }
  end

  local args = { "--no-color", "--formatter", "plain", tempFile }

  -- Add options if provided  
  if options.strict then  
    table.insert(args, "--std")  
    table.insert(args, "lua51")  
  end  
  if options.unused then  
    table.insert(args, "-u")  
  end 
  
  if options.globals then
    table.insert(args, "--globals")
    for _, v in ipairs( options.globals ) do
      table.insert(args,  v)
    end
    -- Default global variables
    local default={"_CTX", "mls","LOG_ENABLE","asset","clientStore","codewidget","command","config","datastore","editor","encoding","event","global","http","index","js","jsonschema","language","lua","library","markdown","math","mq","net","os","service","shell","slashcommand","space","spacelua","string","sync","system","table","template","widget","yaml"}
    for _, v in ipairs( default ) do
      table.insert(args,  v)
    end
  end

   if options.allowDefined then
    table.insert(args, "-d")
  end
  
  local result = shell.run("luacheck", args)
  space.deleteFile(tempFile)

  local output = {
    success = false,
    output = result.stdout or "",
    issues = {}
  }

  if result.code == 0 then
    output.success = true
    if output.output == "" then
      output.output = "No issues found"
    end
    return output
  end

  -- Parse luacheck output using JS regex (recommended)
  for match in string.matchRegexAll(
    output.output,
    "(.+?):(\\d+):(\\d+):\\s+(.*)"
  ) do
    table.insert(output.issues, {
      file = match[1],
      line = tonumber(match[3]),
      column = tonumber(match[4]),
      message = match[5]
    })
  end

  if result.stderr and result.stderr ~= "" then
    output.output = output.output .. "\n\nStderr:\n" .. result.stderr
  end

  return output
end
```

## Changelog

* 2026-01-04 feat: linter call
## Community

[Silverbullet forum](https://community.silverbullet.md/t/mindmap-with-markmap-js/1556/7)