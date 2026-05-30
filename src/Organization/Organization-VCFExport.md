---
author: malys
description: Generate VCF of company's employees.
pageDecoration.prefix: "🆘 "
name: "Library/Malys/Organization-VCFExport"
tags: meta/library
---
# VCF exporter
Export `Employees` template to an unique VCF file.

Use with:
- Organization-Employee:  employee card

```space-lua

local function join(tbl, sep)
    return table.concat(tbl, sep or ", ")
end

local function cleanAndLower(str)
  if str ~= nil and #str>1 then
    local cleaned = str:gsub("[éè]", "e")
    cleaned = cleaned:gsub("[^%w]", "")
    return cleaned:lower()
  end
  return ""
end

local function generatePerson(person, path)
    local uml={}
    table.insert(uml, "BEGIN:VCARD")
    table.insert(uml, "VERSION:3.0")
    table.insert(uml, "FN:"..person.first_name.." "..person.last_name)
    table.insert(uml, "EMAIL;TYPE=INTERNET;TYPE=WORK:"..cleanAndLower(person.first_name).."."..cleanAndLower(person.last_name).."@scopandco.fr")
    table.insert(uml, "END:VCARD") 
    return table.concat(uml, "\n")
end

local function children(path)
    local crumbsChildren = {}
    local mypage = path or editor.getCurrentPage()
    for page in each(table.sort(space.listPages(), compareDate)) do
        if (string.find(page.name,mypage) and mypage ~= page.name)
        then
              table.insert(crumbsChildren, {name = page.ref})
        end
    end
    return crumbsChildren
end

local function getFrontMatter(page)
    return index.extractFrontmatter(space.readPage(page)).frontmatter
end 

local function organizationVcf(path)
  path = path or editor.getCurrentPage()
  local uml = {}
  local liste= children(path)
  for i,pag in ipairs(liste) do
        local frontM= getFrontMatter(pag.name)
        if frontM ~= nil and frontM.person ~= nil then
          local person = frontM.person
          table.insert(uml, generatePerson(person,path))
        end
  end
  table.insert(uml, "")
  local result= table.concat(uml, "\n")  
  return result
end

slashcommand.define {
  name = "organizationvcf",
  run = function()
    editor.insertAtCursor(organizationVcf(config.get("organization.vcf.export.path")), false, true)
  end
}
```

## Changelog

* 2026-05-29:
  * fix: `cleanAndLower` ran every `gsub` against the original `str`, discarding all but the last; now chains the replacements (accents → strip non-word → lowercase) for valid email local parts
  * cleanup: dropped the unused `source`/`uml` parameter from `generatePerson`
  * cleanup: made `children`, `getFrontMatter`, `organizationVcf` local to avoid global collisions with Organization-Chart
  * cleanup: removed leftover `print(result)` debug call

