---
author: malys
description: Dark theme thought for readibility and productivity
name: "Library/Malys/theme-malys"
tags: meta/library
---
# Malys theme

Dark theme thought for readability and productivity.

## Example
# 1 
## 2
### 3
#### 4
##### 5
###### 6

`code`

*emphasis*  

**strong**

## Editor

```space-style
html {
  --ui-font: firacode-nf, sans-serif !important;
  --editor-font: firacode-nf  , sans-serif !important;
  --editor-width: 99.9% !important;
  line-height: 1 !important;
}

.markmap {
  --markmap-text-color: #BBDEFB !important;
}

#sb-main .cm-editor {
  font-size: 15px;
  margin-top: 2rem;
}

.sb-line-h1 {
  font-size: 1.8em !important;
  color: #ee82ee !important;
}
.sb-line-h2 {
  font-size: 1.6em !important;
  color: #6a5acd !important;
}
.sb-line-h3 {
   font-size: 1.4em !important;
  color: #4169e1 !important;
}
.sb-line-h4 {
  font-size: 1.2em !important;
  color: #008000 !important;
}
.sb-line-h5 {
  font-size: 1em !important;
  color: #ffff00 !important;
}
.sb-line-h6 {
  font-size: 1em !important;
  color: #ffa500 !important;
}
.sb-line-h1::before {
  content: "h1";
  margin-right: 0.5em;
  font-size: 0.5em !important;
}

.sb-line-h2::before {
  content: "h2";
  margin-right: 0.5em;
  font-size: 0.5em !important;
}

.sb-line-h3::before {
  content: "h3";
  margin-right: 0.5em;
  font-size: 0.5em !important;
}

.sb-line-h4::before {
  content: "h4";
  margin-right: 0.5em;
  font-size: 0.5em !important;
}

.sb-line-h5::before {
  content: "h5";
  margin-right: 0.5em;
  font-size: 0.5em !important;
}

.sb-line-h6::before {
  content: "h6";
  margin-right: 0.5em;
  font-size: 0.5em !important;
}


.sb-code {
  color: grey !important;
}
.sb-emphasis {
  color: darkorange !important;
}
.sb-strong {
  color: salmon !important;
}

html {
  --treeview-phone-height: 25vh;
  --treeview-tablet-width: 25vw;
  --treeview-tablet-height: 100vh;
  --treeview-desktop-width: 20vw; 
}

.sb-bhs {
  height: var(--treeview-phone-height);
}
```

## Treeview
```space-style
.tree__label > span {
  font-size: calc(11px + 0.1vh);
}

@media (min-width: 960px) {
  #sb-root:has(.sb-lhs) #sb-main,
  #sb-root:has(.sb-lhs) #sb-top {
    margin-left: var(--treeview-tablet-width);
  }

  .sb-lhs {
    position: fixed;
    left: 0;
    height: var(--treeview-tablet-height);
    width: var(--treeview-tablet-width);
    border-right: 1px solid var(--top-border-color);
  }
}

@media (min-width: 1440px) {
  #sb-root:has(.sb-lhs) #sb-main,
  #sb-root:has(.sb-lhs) #sb-top {
    margin-left: var(--treeview-desktop-width);
  }

  .sb-lhs {
    width: var(--treeview-desktop-width);
  }
}
```

.tree__label > span {
    padding: 0 5px;
    font-size: 11px;
    line-height: 1.2;
}
.treeview-root {
    --st-label-height: auto;
    --st-subnodes-padding-left: 0.1rem;
    --st-collapse-icon-height: 2.1rem;
    --st-collapse-icon-width: 1.25rem;
    --st-collapse-icon-size: 1rem;
}

## Outline

```space-style
div.cm-scroller {
  scroll-behavior: smooth;
  scrollbar-width: thin;
}
```

## Codemirror

````space-style
<script>  
// Add line numbers to all code blocks  
document.addEventListener('DOMContentLoaded', () => {  
  document.querySelectorAll('.sb-line-fenced-code .sb-code').forEach(codeEl => {  
    const lines = codeEl.textContent.split('\n');  
    codeEl.innerHTML = lines.map((line, i) =>   
      `<div style="position: relative"><span style="position: absolute; left: -3em; width: 2.5em; text-align: right; color: var(--editor-meta-color); opacity: 0.5; font-size: 0.9em; user-select: none">${i+1}</span>${line}</div>`  
    ).join('\n');  
  });  
});  
</script>
/* Line numbers for fenced code blocks */  
.sb-line-fenced-code {  
  position: relative;  
  padding-left: 3.5em;  
}  
  
.sb-line-fenced-code .sb-code {  
  counter-reset: line;  
  white-space: pre;  
}  
  
.sb-line-fenced-code .sb-code > div {  
  counter-increment: line;  
  position: relative;  
}  
  
.sb-line-fenced-code .sb-code > div::before {  
  content: counter(line);  
  position: absolute;  
  left: -3em;  
  width: 2.5em;  
  text-align: right;  
  color: var(--editor-meta-color);  
  opacity: 0.5;  
  font-size: 0.9em;  
  user-select: none;  
}  
  
/* Hide line numbers for inline code */  
:not(.sb-line-fenced-code) > .sb-code::before {  
  display: none !important;  
}
```