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
-- priority: 15
mls = mls or {}

if library~=nil and (mls == nil or (mls ~= nil and mls.debug == nil)) then
	library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities.md")
	editor.flashNotification("'Depencies' has been installed", "Info")
end

-- Template to run luacheck on Lua code and format results
mls.luacheck = function(code, options)
  options = options or {}
  local codeEncoded= encoding.base64Encode(code)
  local args = { "--no-color", "--formatter", "plain" }
  -- Add options if provided
  if options.ignore ~= nil and type(options.ignore) == "table" then 
      table.insert(args, "-i")  
      table.appendArray(args, table.map(options.ignore, tostring))
  end  
  if options.strict then  
    table.insert(args, "--std")  
    table.insert(args, "lua54")  --lua version embedded
  end  
  if options.unused then  
    table.insert(args, "-u")  
  end 

  if options.globals ~= nil and type(options.globals) == "table" then
    table.insert(args, "--globals")
    -- Default global variables
    local default_prefixes=table.appendArray({"mls","LOG_ENABLE"},options.globals)
    table.appendArray(args,default_prefixes)
   end

   if options.allowDefined then
    table.insert(args, "-d")
  end

  local cmdArgs= {"-c", "echo ' "..codeEncoded.." ' | base64 -d | luacheck - ".. table.concat(args," ")}
  --js.window.navigator.clipboard.writeText(table.concat(cmdArgs))
  local result = shell.run("sh",cmdArgs)   
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

* 2026-01-20 feat: support `ignore` argument
* 2026-01-04 feat: linter call
## Community

[Silverbullet forum](https://community.silverbullet.md/t/feature-tooling-to-debug-and-develop/3712)