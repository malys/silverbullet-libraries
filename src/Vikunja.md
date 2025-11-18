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
    from getVikunjaTasks() 
    where due_date <= date.nextmonth()
    order by due_date
  ]], templates.vikunjaRecurringTasks
)}
```


```space-lua
function getVikunjaTasks(criteria)
  local baseUrl =  config.get("vikunja").baseUrl
  local c=criteria
  if c==nil then
    c="/tasks/all?filter=done=false"
  end
  local token = config.get("vikunja").token
  local apiUrl = (baseUrl .. "api/v1" .. c )
  print(apiUrl)
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
    return "Not OK response"
  end
end

templates.vikunjaRecurringTasks = function(task)
  local function convert_date(date)
    return date:sub(1,10)
  end
    
  return string.format("* [Link](" .. baseUrl .. "tasks/%s) [due: %s] %s", task.id, convert_date(task.due_date), task.title ) .. "\n"
end
```

${config.get("vikunja")}
