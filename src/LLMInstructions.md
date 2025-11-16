---
author: malys
description: System prompt to pilot LLM in SB plugin coding.
name: "Library/Malys/LLMInstructions"
tags: meta/library
---
# Instructions

> **tip** Hint
> > I use [a RAG with silverbullet source code](https://deepwiki.com/silverbulletmd/silverbullet).  It’s probably not the most powerful LLM, but it’s aware of source code.


```
I want to generate a space-lua  for [silverbullet](https://silverbullet.md/). space-lua language inherits from lua language with some specifc API. Please, follows thoses rules:
- not use "pcall"
- not use javascript library by default
- if function debug_log exists, every function must be surrounded by debug_log
- not use lua standard methods but space-lua silverbullet api (https://silverbullet.md/API)
  - string.byte(s, i?, j?)
  - string.char(...)
  - string.find(s, pattern, init?, plain?)
  - string.format(format, ...)
  - string.gsub(s, pattern, repl, n?)
  - string.match(s, pattern, init?)
  - string.gmatch(s, pattern)
  - string.len(s)
  - string.lower(s)
  - string.upper(s)
  - string.rep(s, n, sep?)
  - string.reverse(s)
  - string.sub(s, i, j?)
  - string.split(s, sep)
  - string.startsWith(s, prefix)
  - string.endsWith(s, suffix)
  - string.trim(s)
  - string.trimStart(s)
  - string.trimEnd(s)
  - string.matchRegex(s, pattern)
  - string.matchRegexAll(s, pattern)
- use "local" functions and variables as it's possible
- every function should be testable
- add comments for every functions
- add comment header to explain the goal of  the generated program
```