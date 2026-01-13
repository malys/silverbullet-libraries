---
author: malys
description:  LRU cache leveraging @isaacs/lrucache
name: "Library/Malys/LRU"
tags: meta/library
---
# LRU cache manager

This script (`mls.cache.lru`) wraps the JavaScript [@isaacs/lrucache](https://github.com/isaacs/node-lru-cache) library, allowing Lua code to utilize a LRU cache with methods for setting, getting, and managing cached data with automatic expiration.

> **warning** Caution
> On system start a globally accessible cache manager `mls.cache.lru.CacheManager` is created. This allows other parts of the application to easily utilize a pre-configured LRU cache.
> Default configuration is:
> max entries: 100

## Features

- LRU eviction
- TTL support
- Fetch-on-miss
- Serialization (dump/load)
- Snapshot iteration
- Global preconfigured cache
- 
## Use

```lua
-- Set
mls.cache.lru.CacheManager.set(1,"amazing")
-- Get
mls.cache.lru.CacheManager.get(1) 
-- Has
mls.cache.lru.CacheManager.has(1)
-- Entries
mls.cache.lru.CacheManager.entries()
-- Keys
mls.cache.lru.CacheManager.keys()
-- Values
mls.cache.lru.CacheManager.values() 
-- Delete
mls.cache.lru.CacheManager.delete(1)
-- Size
mls.cache.lru.CacheManager.size()

-- Fetch-on-miss
mls.cache.lru.CacheManager.fetch("user:1", {
  fetchMethod = function()
    return loadUserFromDB()
  end,
  ttl = 60_000
})

-- Serialize cache
local snapshot = mls.cache.lru.CacheManager.dump()
mls.cache.lru.CacheManager.clear()
mls.cache.lru.CacheManager.load(snapshot)
```

## Code


```space-lua
-- priority: 15
-- Global namespace
mls = mls or {}
mls.cache = mls.cache or {}
mls.cache.lru = mls.cache.lru or {}

local function log(...)
	if LOG_ENABLE and mls and mls.debug then
		if type(mls.debug) == "function" then
			mls.debug(table.concat({
				...
			}, " "))
		end
	end
end


```
## Changelog

* 2026-01-03  wrapper init

## Community

[Silverbullet forum]([https://community.silverbullet.md/t/space-lua-addon-with-missing-git-commands-history-diff-restore/3539](https://community.silverbullet.md/t/mindmap-with-markmap-js/1556))