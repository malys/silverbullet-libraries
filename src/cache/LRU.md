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
mls.cache.lru.CacheManager.keys() }
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
--priority: 15
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

-- Factory function
function mls.cache.lru.new(options)
	local opts = options or {}
  -- Import JS TTLCache
	local cacheManager = js.import("https://esm.sh/lru-cache")
	local jsCache = js.new(cacheManager.LRUCache, js.tojs(opts))
	log("Instance")
	local cache = {
		_js = jsCache
	}

  -- size
	function cache.size()
		log("size")
		return js.tolua(jsCache.size)
	end

  -- set
	function cache.set(key, value, options)
		log("set")
    	local opts = options or {}
		return jsCache.set(key, value, opts)
	end

  -- get
	function cache.get(key, options)
		log("get")
    	local opts = options or {}
		return js.tolua(jsCache.get(key, opts))
	end

  -- has
	function cache.has(key)
		log("has")
		return js.tolua(jsCache.has(key))
	end

  -- delete
	function cache.delete(key)
		log("delete")
		return jsCache.delete(key)
	end

  -- clear
	function cache.clear()
		log("clear")
		return jsCache.clear()
	end

  -- remaining TTL
	function cache.remainingTTL(key)
		log("remain")
		return js.tolua(jsCache.getRemainingTTL(key))
	end

  -- cancel timer
	function cache.cancelTimer()
		log("cancel")
		return jsCache.cancelTimer()
	end

  -- entries (Lua snapshot)
	function cache.entries()
		log("entries")
		local out = {}
		local generator = jsCache.entries()
		for i = 1, jsCache.size, 1 do
			local v = generator.next().value
			out[v[1]] = v[2]
		end
		return out
	end

  -- keys (Lua snapshot)
	function cache.keys()
		log('keys')
		local out = {}
		local generator = jsCache.keys()
		for i = 1, jsCache.size, 1 do
			local v = generator.next().value
			table.insert(out, v)
		end
		return out
	end

  -- values (Lua snapshot)
	function cache.values()
		log("values")
		local out = {}
		local generator = jsCache.values()
		for i = 1, jsCache.size, 1 do
			local v = generator.next().value
			table.insert(out, v)
		end
		return out
	end
	return cache
end

  -- peek (no recency update)
function cache.peek(key)
	log("peek")
	return js.tolua(jsCache.peek(key))
end

  -- pop (remove least-recently-used)
function cache.pop()
	log("pop")
	return js.tolua(jsCache.pop())
end

  -- fetch (async-aware JS method, sync wrapper)
function cache.fetch(key, options)
	log("fetch")
	local opts = options or {}
	return js.tolua(jsCache.fetch(key, js.tojs(opts)))
end

  -- forEach (oldest → newest)
function cache.forEach(fn)
	log("forEach")
	jsCache.forEach(js.new(js.Function, function(value, key)
		fn(key, js.tolua(value))
	end))
end

  -- rforEach (newest → oldest)
function cache.rforEach(fn)
	log("rforEach")
	jsCache.rforEach(js.new(js.Function, function(value, key)
		fn(key, js.tolua(value))
	end))
end

  -- purge stale entries
function cache.purgeStale()
	log("purgeStale")
	return jsCache.purgeStale()
end

  -- info about a key
function cache.info(key)
	log("info")
	return js.tolua(jsCache.info(key))
end

  -- dump cache (serialization)
function cache.dump()
	log("dump")
	return js.tolua(jsCache.dump())
end

  -- load cache dump
function cache.load(entries)
	log("load")
	return jsCache.load(js.tojs(entries))
end

  -- resize cache
function cache.resize(max)
	log("resize")
	return jsCache.resize(max)
end

  -- readonly properties
function cache.max()
	return js.tolua(jsCache.max)
end
function cache.calculatedSize()
	return js.tolua(jsCache.calculatedSize)
end


-- Default LRU cache to max 1000
mls.cache.lru.CacheManager = mls.cache.lru.new({
	max = 100
})
```

## Changelog

* 2026-01-03  wrapper init

## Community

[Silverbullet forum]([https://community.silverbullet.md/t/space-lua-addon-with-missing-git-commands-history-diff-restore/3539](https://community.silverbullet.md/t/mindmap-with-markmap-js/1556))