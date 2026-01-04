---
author: malys
description: Vikunja, open-source project management tool, integration.
name: "Library/Malys/Vikunja"
tags: meta/library
---
# Vikunja 
[Vikunja](https://vikunja.io/): *The* free and open-source project management tool.

> **warning** Caution
> **Depends on** [Utilities.md](https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities.md) and [TTL cache](https://github.com/malys/silverbullet-libraries/blob/main/src/cache/TTL.md). They will be installed automatically.


## Configuration
```toml
# Check network queries in browser to define userId &  projectId
# Configuration
 vikunja ={
      baseUrl="https://vikunja.your.domain",
      token="token",
  }
```
```lua
${template.each(
  query[[
    from vikunja.get() 
    where due_date <= date.nextmonth()
    order by due_date
  ]], vikunja.template
)}
```

## Code


```space-lua
local function log(...)
	if LOG_ENABLE and mls and mls.debug then
		if type(mls.debug) == "function" then
			mls.debug(table.concat({
				...
			}, " "))
		end
	end
end
--local cond3 = (mls ~= nil and mls.cache ~= nil and mls.cache.ttl == nil)
--if mls == nil or (mls ~= nil and mls.debug == nil) or (mls ~= nil and mls.cache == nil) or cond3 then
--	library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities.md")
--	library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/cache/TTL.md")
--	editor.flashNotification("'Depencies' has been installed", "Info")
--end

vikunja = {}
-- priority: 9
config.define("vikunja", {
	type = "object"
})
-- Select language first
local vik = config.get("vikunja") or ""
if vik == "" then
	editor.flashNotification("Vikunja: Configuration is missing!", "error")
	vikunja.baseUrl = "missing"
else
	local baseUrl = config.get("vikunja").baseUrl .. "/"
	string.sub(baseUrl, "//", "/")
	vikunja.baseUrl = baseUrl
end

vikunja.get = function (criteria)
	log("GET")
	local c = criteria
	if c == nil then
		c = "done=false"
	end
	local token = config.get("vikunja").token
	local apiUrl = (vikunja.baseUrl .. "api/v1/tasks/all?filter=" .. c)
	local result = mls.cache.ttl.CacheManager.get("VKJ_" .. c)
	log(result)
	if result == nil then
		local response = http.request(
      apiUrl, {
			method = "GET",
			headers = {
				Authorization = "Bearer " .. token,
				Accept = "application/json",
			}
		})
		if response.ok then
			result = response.body
			mls.cache.ttl.CacheManager.set("VKJ_" .. c, result)
		else
			result = {
				id = "0",
				title = "No response" .. response
			}
		end
	end
	return result
end

vikunja.template = function(task)
	local due = ""
	local short = task.due_date:sub(1, 10)
	if short ~= "0001-01-01" then
		due = "(" .. short .. ")"
	end
	local result = string.format("* [Link](" .. vikunja.baseUrl .. "tasks/%s) %s %s", task.id, due, task.title) .. "\n"
	return result
end
```

## Fields

* id
* title
* description
* done
* done_at
* due_date
* reminders
* project_id
* repeat_after
* repeat_mode
* priority
* start_date
* end_date
* assignees
* labels
* hex_color
* percent_done
* identifier
* index
* related_tasks
* attachments
* cover_image_attachment_id
* is_favorite
* created
* updated
* bucket_id
* position
* reactions
* created_by


## Community

[Silverbullet forum](https://community.silverbullet.md/t/pull-in-vikunja-tasks/3324)
