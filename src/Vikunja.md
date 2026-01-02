---
author: malys
description: Vikunja, open-source project management tool, integration.
name: "Library/Malys/Vikunja"
tags: meta/library
---
# Vikunja 
[Vikunja](https://vikunja.io/): *The* free and open-source project management tool.

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


```space-lua
vikunja={}
-- prioity: 9
config.define("vikunja", {
    type = "object"
})

-- Select language first
local vik = config.get("vikunja") or ""
if vik == "" then 
  editor.flashNotification("Vikunja: Configuration is missing!","error")
  vikunja.baseUrl="missing"
else 
  local baseUrl =config.get("vikunja").baseUrl.."/"
  string.sub(baseUrl,"//","/")
  vikunja.baseUrl=baseUrl
end

vikunja.get=function (criteria)
  print(vikunja)
  local c=criteria
  if c==nil then
    c="done=false"
  end
  local token = config.get("vikunja").token
  local apiUrl = (vikunja.baseUrl .. "api/v1/tasks/all?filter=" .. c )
  local response = http.request(
    apiUrl, {
    method = "GET",
    headers = {
      Authorization = "Bearer " .. token,
      Accept = "application/json",
    }
  })
  if response.ok then 
    return response.body
  else 
    return {id="0",title="No response"..response}
  end
end


vikunja.template = function(task)
  local due =""
  local short=task.due_date:sub(1,10)
  if short~= "0001-01-01" then
     due="("..short..")" 
  end
  local result=string.format("* [Link]("..vikunja.baseUrl.."tasks/%s) %s %s", task.id, due , task.title ) .. "\n"
  return result
end
```
${template.each(
  query[[
    from vikunja.get() 
    where done
  ]], vikunja.template
)}
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
