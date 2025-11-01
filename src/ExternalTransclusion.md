---
author: malys
description: Transclude data form external resource.
---
# External transclusion
Transclude data form external resource.

* [TODO] Replace with new internal function  


${ transclude "https://raw.githubusercontent.com/dair-ai/Prompt-Engineering-Guide/refs/heads/main/pages/techniques/zeroshot.en.mdx" }


```space-lua
transclude = function(url)
  local result = http.request(url)
  local tree = markdown.parseMarkdown(result.body)
  local rendered = markdown.renderParseTree(tree)
  return widget.new { markdown = rendered:gsub("<[^>]*>","") }
end
```

