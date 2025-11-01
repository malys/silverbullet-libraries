---
author: malys
description: universal palette (as VScode Palette), use '>' to execute commands
---

# Universal Palette

The VSCode Palette feature allows you to search and open content items (pages, commands, etc.) quickly. 
You can customize the objects to populate, like page, command, etc. 
The palette is a unique feature that provides a quick way to navigate your content.
You can search directly page and header and use “>“ to execute commands.  

```space-lua
-- VSCode-style palette with nil safety  
local vscode = {}  
vscode.enabledObjectToPopulate = {"page", "command", "header"}  
vscode.cacheTimeout = 30 * 60  
vscode.maxItems = 200  
vscode.truncate=80
vscode.usageHistory = {}  
  
-- Load usage history from datastore with nil check  
local function loadUsageHistory()  
    local stored = datastore.get({"vscode:usageHistory"})  
    if stored and type(stored) == "table" then  
        vscode.usageHistory = stored  
    else  
        vscode.usageHistory = {}  
    end  
end  
  
-- Get usage timestamp for sorting with nil check  
local function getUsageTime(ref)  
    if not vscode.usageHistory then  
        return 0  
    end  
    return vscode.usageHistory[ref] or 0  
end  

local function generateCategory(name)  
  local colonIndex = string.find(name, "/")  
  if colonIndex and colonIndex > 1 then  
    return string.sub(name, 1, colonIndex - 1)  
  end  
  return name  
end 

local function generateRest(name)  
  local colonIndex = string.find(name, "/")  
  if colonIndex and colonIndex > 1 then  
    return string.sub(name,  colonIndex +1)  
  end  
  return name  
end 
  
local function populate()  
    local success, options = pcall(function()  
        local opts = {}  
          
        -- Pages with nil check  
        if table.includes(vscode.enabledObjectToPopulate, "page") then  
            local pages = query[[  
                from index.tag "page"   
                where not ref:startsWith("Library")   
                select {name=name, ref=ref, lastModified=lastModified}  
                order by lastModified desc  
                limit vscode.maxItems  
            ]]  
              
            -- Add nil check for query results  
            if pages and type(pages) == "table" then  
                for _, item in ipairs(pages) do  
                    if item and item.name then  -- Check item is not nil  
                        category= generateCategory(item.ref)
                        name= generateRest(item.name)
                        table.insert(opts, {  
                            name = name,  
                            prefix= "📄" , 
                          --  description = item.ref or "",  
                            ref = item.ref,  
                            type = "page",  
                            category= category  ,
                            orderId = getUsageTime(item.ref)  
                        })  
                    end  
                end  
            end  
        end  

 -- Header with nil check  
        if table.includes(vscode.enabledObjectToPopulate, "header") then  
            local pages = query[[  
                from index.tag "header"   
                where not ref:startsWith("Library")   
                select {name=name, ref=ref, lastModified=lastModified}  
                order by lastModified desc  
                limit vscode.maxItems  
            ]]  
              
            -- Add nil check for query results  
            if pages and type(pages) == "table" then  
                for _, item in ipairs(pages) do  
                    if item and item.name and #item.name>0  then   
                        category="header"
                        name= string.sub(item.name,1,vscode.truncate)
                        table.insert(opts, {  
                            name = name,  
                            prefix= "✨" , 
                          --  description = item.ref or "",  
                            ref = item.ref,  
                            type = "header",  
                            category= category  ,
                            orderId = getUsageTime(item.ref)  
                        })  
                    end  
                end  
            end  
        end  
      
        -- Commands with nil check  
        if table.includes(vscode.enabledObjectToPopulate, "command") then  
            local commands = system.listCommands()  
              
            -- Add nil check for commands  
            if commands and type(commands) == "table" then  
                for name, def in pairs(commands) do  
                    if name and #name > 2 and def then  -- Check all values  
                        local shortcut = def.key or def.mac or ""  
                        local category, action = string.match(name, "^([^:]+):%s*(.+)$")  
                        local description= def.description or "" 
                          
                        local displayName  
                        if category and action then  
                            displayName = ">" .. action  
                        else  
                            displayName = ">" .. name  
                        end  
                          
                        if shortcut ~= "" then  
                            description = description .. " " .. shortcut  
                        end  
                          
                        table.insert(opts, {  
                            name = displayName,  
                            description = description,
                            ref = name,  
                            type = "command",
                            category= category,
                            prefix= "🎯",  
                            orderId = getUsageTime(name)  
                        })  
                    end  
                end  
            end  
        end  
          
        -- Sort by orderId  
        if #opts > 0 then  
            table.sort(opts, function(a, b)  
                return (a.orderId or 0) > (b.orderId or 0)  
            end)  
        end  
          
        return opts  
    end)  
      
    if not success then  
        editor.flashNotification("Error loading palette: " .. tostring(options), "error")  
        return {}  
    end  
      
    return options or {}  
end  
  
-- Initialize with nil safety  
loadUsageHistory()  
vscode.entries = populate()  
vscode.previousCheck = os.time()  
  
command.define {  
    name = "Universal Palette",  
    key = "Ctrl-p",  
    priority = 10,  
    run = function()  
        if not vscode.entries or #vscode.entries == 0 then  
            vscode.entries = populate()  
        end  
          
        local selected = editor.filterBox(  
            "🎨 Quick Open",  
            vscode.entries,  
            "🔍 Type '>' for commands",  
            "Type to search..."  
        )  
          
        if selected and selected.ref then  -- Check selected is not nil  
            -- Record usage  
            if vscode.usageHistory then  
                vscode.usageHistory[selected.ref] = os.time()  
                datastore.set({"vscode:usageHistory"}, vscode.usageHistory)  
            end  
              
            if selected.type == "command" then  
                editor.invokeCommand(selected.ref)  
            else  
                editor.navigate(selected.ref)  
            end  
              
            -- Refresh for next time  
            vscode.entries = populate()  
        end  
    end  
}
```

