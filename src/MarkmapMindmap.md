---
author: malys
description:  MarkMap mindmap integration.
name: "Library/Malys/MarkmapMindmap"
tags: meta/library
---
# Markmap mindmap
 
This library provides a way to preview your [MarkMap](https://markmap.js.org/) mind map in a panel while you are editing your space.

With MarkMap Preview, you can:
- Preview your slides without leaving the context of your space
- See how your slides look in real-time as you modify your markdown
- Use the MarkMap Preview panel to navigate through your slides and see them in action
![](https://community.silverbullet.md/uploads/default/original/2X/4/493e4db01035bc5d0ef5189f8f502ac7fc449709.gif)

## Disclaimer & Contributions

This code is provided **as-is**, **without any kind of support or warranty**.  
I do **not** provide user support, bug-fixing on demand, or feature development.

If you detect a bug, please **actively participate in debugging it** (analysis, proposed fix, or pull request) **before reporting it**. Bug reports without investigation may be ignored.

🚫 **No new features will be added.**  
✅ **All types of contributions are welcome**, including bug fixes, refactoring, documentation improvements, and optimizations.

By using or contributing to this project, you acknowledge and accept these conditions.


## Configuration

To easily manage JS code source, we use a dynamic introspection mechanism based on md page path.
If you don’t install program to default path `Library/Malys/xxx`,we have to set:

```lua
config.set("markmap.source ","xxxx")
-- ex: config.set("markmap.source ","Library/Malys/MarkmapMindmap")
-- where xxx is the path of MarkmapMindmap md page
```

> **warning** Caution
> **Depends on** [Utilities.md](https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities.md). It will be installed automatically.


## Code

 ```space-lua
local is_panel_visible = false
local current_panel_id = config.get("markmap.panelPosition") or "rhs"
-- Function to render Marp slides
local function render(mode)  
    local source=config.get("markmap.source") or "Library/Malys/MarkmapMindmap"
    local panelSize=config.get("markmap.panelSize") or 4
    if library~=nil and (mls == nil or (mls ~=nil and mls.debug == nil)) then 
      library.install("https://github.com/malys/silverbullet-libraries/blob/main/src/Utilities.md")
      editor.flashNotification("'Utilities' has been installed", "Info")
    end
    if (not is_panel_visible and mode) or (not mode and is_panel_visible) then
      -- Get the current page content
      local page_content = editor.getText()
      --  mls.debug("page_content: "..page_content)
      local contentBase64=encoding.base64Encode(page_content)
      local content1= mls.getCodeBlock(source,"innerHTML","@CONTENT@", contentBase64)
      local js = mls.getCodeBlock(source,"jsInject","@CONTENT@",content1)      
      local panel_html= mls.getCodeBlock(source,"template")
      
      editor.showPanel(current_panel_id,panelSize,  panel_html, js)
      is_panel_visible = true
    else
        -- Hide the panel if it's visible
        editor.hidePanel(current_panel_id)
        is_panel_visible = false
    end
end

-- Define the command
command.define({
    name = "Markmap: Toggle preview",
    description = "Toggle Marp slides render in a panel",
    run = function(e)
      render(true)
    end
})

-- Listen for page modifications
event.listen({
    name = "editor:pageSaved",
    run = function(e)
      render(false)
    end
})
```


## JS templates
```js jsInject
const scriptId = "markmap-inject";

// Remove existing script if present
const existingScript = document.getElementById(scriptId);
if (existingScript) {
  existingScript.remove();
}

// Create and inject the script again
const script = document.createElement("script");
script.type = "module";
script.id = scriptId;
script.textContent = `@CONTENT@`;
document.documentElement.appendChild(script);
```
```js innerHTML  
function b64DecodeUnicode(str) {
  return decodeURIComponent(
    atob(str)
      .split("")
      .map(c => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join("")
  );
}

import { Transformer } from "https://esm.sh/markmap-lib?bundle";
import { Markmap, deriveOptions } from "https://esm.sh/markmap-view?bundle";
import { Toolbar } from "https://esm.sh/markmap-toolbar?bundle";

const transformer = new Transformer();
const { root } = transformer.transform(b64DecodeUnicode("@CONTENT@"));

const svg = document.getElementById("mindmap");
svg.innerHTML = "";
window.mm = Markmap.create(
  "svg#mindmap",
  deriveOptions(null),
  root
);

const existing = document.getElementsByClassName("mm-toolbar");
if(existing.length==0){

  // 👉 Toolbar
  const toolbar = new Toolbar();
  toolbar.attach(window.mm);
  
  const el = toolbar.render();
  el.style.position = "absolute";
  el.style.bottom = "20px";
  el.style.right = "20px";
document.body.appendChild(el);
}  

// 👉 print
window.addEventListener("beforeprint", () => {
  window.mm?.fit();
});
```


## HTML template

```html template
<style>
        html,
        html {
          overflow-y: scroll !important;
          width: 90% !important;
        }
        @media print {
          .no-print,
          .mm-toolbar {
            display: none !important;
          }
          .markmap-toolbar {
            display: none !important;
          }
          .markmap-dark {
            background: white !important;
            color: black !important;
          }
          * {
            animation: none !important;
            transition: none !important;
          }
         /* Remove default page margins */
          @page {
            margin: 0;
          }
         /* 2️⃣ Reset layout sizing */
          html,
          body {
            margin: 0 !important;
            padding: 0 !important;
            height: auto !important;
            overflow: visible !important;
          }
          /*  Hide all toolbars */
          .no-print,
          .markmap-toolbar {
            display: none !important;
          }
        
        }
        body {
          overflow: initial !important;
          color: var(--top-color);
          font-family: georgia, times, serif;
          font-size: 13pt;
          margin-top: revert;
          margin-bottom: revert;
          padding-left: 20px;
          padding-right: 20px;
        }
        
        img {
          max-width: 100%;
        }
        
        table {
          width: 100%;
          border-spacing: 0;
        }
        
        ul li p {
          margin: 0;
        }
        
        thead tr {
          background-color: var(--editor-table-head-background-color);
          color: var(--editor-table-head-color);
        }
        
        th,
        td {
          padding: 8px;
        }
        
        tbody tr:nth-of-type(even) {
          background-color: var(--editor-table-even-background-color);
        }
        
        a[href] {
          text-decoration: none;
          color: var(--link-color);
        }
        
        blockquote {
          border-left: 1px solid var(--editor-blockquote-border-color);
          margin-left: 2px;
          padding-left: 10px;
          background-color: var(--editor-blockquote-background-color);
          color: var(--editor-blockquote-color);
        }
        
        hr {
          margin: 1em 0 1em 0;
          text-align: center;
          border-color: var(--editor-ruler-color);
          border-width: 0;
          border-style: dotted;
        }
        
        hr:after {
          content: "···";
          letter-spacing: 1em;
        }
        
        span.highlight {
          background-color: var(--highlight-color);
        }
        
        .markmap {
            --markmap-a-color: #0097e6;
            --markmap-a-hover-color: #00a8ff;
            --markmap-highlight-bg: #ffeaa7;
        
            --markmap-code-bg: #fff;
            --markmap-code-color: #555;
            --markmap-circle-open-bg: #fff;
            --markmap-text-color: #333;
        }
        
        html[data-theme=dark] {
        .markmap {
            --markmap-code-bg: #1a1b26;
            --markmap-code-color: #ddd;
            --markmap-circle-open-bg: #444;
            --markmap-text-color: #dddbdb;
          }
        }
        * {
          margin: 0;
          padding: 0;
        }
        #mindmap {
          display: block;
          width: 100vw;
          height: 100vh;
        }
  
        .mm-toolbar {display:flex;-webkit-user-select:none;-moz-user-select:none;user-select:none;align-items:center;border-width:1px;--un-border-opacity:1;border-color:rgb(212 212 216 / var(--un-border-opacity));border-radius:0.25rem;border-style:solid;--un-bg-opacity:1;background-color:rgb(255 255 255 / var(--un-bg-opacity));padding:0.25rem;line-height:1;        }
          .mm-toolbar:hover {--un-border-opacity:1;border-color:rgb(161 161 170 / var(--un-border-opacity));          }
          .mm-toolbar svg {display:block;          }
          .mm-toolbar a {display:inline-block;text-decoration:none;          }
          .mm-toolbar-brand > img {width:1rem;height:1rem;vertical-align:middle;            }
          .mm-toolbar-brand > span {padding-left:0.25rem;padding-right:0.25rem;            }
          .mm-toolbar-brand:not(:first-child), .mm-toolbar-item:not(:first-child) {margin-left:0.25rem;            }
          .mm-toolbar-brand > *, .mm-toolbar-item > * {min-width:1rem;cursor:pointer;text-align:center;font-size:0.75rem;line-height:1rem;--un-text-opacity:1;color:rgb(161 161 170 / var(--un-text-opacity));            }
          .mm-toolbar-brand.active,
          .mm-toolbar-brand:hover,
          .mm-toolbar-item.active,
          .mm-toolbar-item:hover {border-radius:0.25rem;--un-bg-opacity:1;background-color:rgb(228 228 231 / var(--un-bg-opacity));            }
          .mm-toolbar-brand.active > *, .mm-toolbar-brand:hover > *, .mm-toolbar-item.active > *, .mm-toolbar-item:hover > * {--un-text-opacity:1;color:rgb(39 39 42 / var(--un-text-opacity));              }
          .mm-toolbar-brand.active, .mm-toolbar-item.active {--un-bg-opacity:1;background-color:rgb(212 212 216 / var(--un-bg-opacity));            }
        
        .markmap-dark .mm-toolbar {--un-border-opacity:1;border-color:rgb(82 82 91 / var(--un-border-opacity));--un-bg-opacity:1;background-color:rgb(39 39 42 / var(--un-bg-opacity));--un-text-opacity:1;color:rgb(161 161 170 / var(--un-text-opacity));        }
        
        .markmap-dark .mm-toolbar:hover {--un-border-opacity:1;border-color:rgb(113 113 122 / var(--un-border-opacity));          }
        
        .markmap-dark .mm-toolbar > *:hover {--un-bg-opacity:1;background-color:rgb(82 82 91 / var(--un-bg-opacity));          }
        
        .markmap-dark .mm-toolbar > *:hover > * {--un-text-opacity:1;color:rgb(228 228 231 / var(--un-text-opacity));       }
      </style>
      <div id="root" class="sb-preview">
      <div class="sb-mindmap-toolbar no-print">
        <button onclick="window.print()" title="Print">
          🖨️
        </button>
      </div>
      <svg id="mindmap"></svg>
      </div>
```

## Changelog

* 2026-01-13: fix: multiple SVG visible on refresh
* 2025-12-01 fix: html duplicate inserts

## Community

[Silverbullet forum]([https://community.silverbullet.md/t/space-lua-addon-with-missing-git-commands-history-diff-restore/3539](https://community.silverbullet.md/t/mindmap-with-markmap-js/1556))