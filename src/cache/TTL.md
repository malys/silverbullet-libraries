---
author: malys
description:  TTL cache leveraging @isaacs/ttlcache
pageDecoration.prefix: "🛠️ "
name: "Library/Malys/TTL"
tags: meta/library
---
# TTL cache manager

This script (`mls.cache.ttl`) wraps the JavaScript [@isaacs/ttlcache](https://github.com/isaacs/ttlcache) library, allowing Lua code to utilize a TTL cache with methods for setting, getting, and managing cached data with automatic expiration.

> **warning** Caution
> On system start a globally accessible cache manager `mls.cache.ttl.CacheManager` is created. This allows other parts of the application to easily utilize a pre-configured TTL cache.
> Default configuration is:
> ttl: 10mn
> max entries: 100

## Use

```lua

-- Set
mls.cache.ttl.CacheManager.set(1,"amazing")
-- Get
mls.cache.ttl.CacheManager.get(1) 
-- Has
mls.cache.ttl.CacheManager.has(1)
-- Entries
mls.cache.ttl.CacheManager.entries()
-- Keys
mls.cache.ttl.CacheManager.keys() }
-- Values
mls.cache.ttl.CacheManager.values() 
-- Delete
mls.cache.ttl.CacheManager.delete(1)
-- Size
mls.cache.ttl.CacheManager.size()
```

## Code


```space-lua
-- luacheck: globals cache jsCache
-- priority: 15
-- Global namespace
mls = mls or {}
mls.cache = mls.cache or {}
mls.cache.ttl = mls.cache.ttl or {}

local function log(...)
  if LOG_ENABLE and mls and mls.debug then
     if type(mls.debug) == "function" then 
       mls.debug(table.concat({...}, " "))
     end  
  end
end

-- Factory function
function mls.cache.ttl.new(opts)
  opts = opts or {}
  -- Import JS TTLCache
  local cacheManager = js.import("https://esm.sh/@isaacs/ttlcache")
  local jsCache = js.new(cacheManager.TTLCache, js.tojs(opts))
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
  function cache.set(key, value, opti)
    log("set")
    opti = opti or {}
    return jsCache.set(key, value, opti)
  end

  -- get
  function cache.get(key, opti)
    log("get")
    opti = opti or {}
    local result= js.tolua(jsCache.get(key, opti))
    log(result)
    return result
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
    local out={}
    local generator = jsCache.entries()
    for i = 1,jsCache.size,1 
    do 
      local v=generator.next().value
      out[v[1]]=v[2]
    end
    return out
  end

  -- keys (Lua snapshot)
  function cache.keys()
    log('keys')
    local out={}
    local generator = jsCache.keys()
    for i = 1,jsCache.size,1 
    do 
      local v=generator.next().value
      table.insert(out,v)
    end
    return out
  end

  -- values (Lua snapshot)
  function cache.values()
    log("values")  
    local out={}
    local generator = jsCache.values()
    for i = 1,jsCache.size,1 
    do 
      local v=generator.next().value
      table.insert(out,v)
    end
    return out
  end

  return cache
end

-- Default TTL cache to 10mn and max 1000
mls.cache.ttl.CacheManager=mls.cache.ttl.new({ ttl = 10* 60* 1000, max = 100})
```

## Changelog

* 2026-02-06:
  * fix: linter issue
* 2026-01-03  wrapper init

## Community

[Silverbullet forum]([https://community.silverbullet.md/t/space-lua-addon-with-missing-git-commands-history-diff-restore/3539](https://community.silverbullet.md/t/mindmap-with-markmap-js/1556))