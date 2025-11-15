---
recommend: ⭐⭐⭐⭐⭐
--githubUrl: "https://github.com/ChenZhu-Xie/xczphysics_SilverBullet/blob/main/STYLE/Theme/HHH.md"
udpateDate: 2025-10-28
---rawUrl: "https://raw.githubusercontent.com/ChenZhu-Xie/xczphysics_SilverBullet/main/STYLE/Theme/HHH.md"
updateDate: "2025-11-01T13:24:02Z"
lastCommitDate: "2025-10-31T09:45:25Z"
author: chenzhu-xie
description: Fork of  "https://github.com/ChenZhu-Xie/xczphysics_SilverBullet/blob/main/STYLE/Theme/HHH.md"
---
  
# HierarchyHighlightHeadings - HHH Theme

## JS Part (Experimental)

### Step 1. Reload your space to load the space-lua from this page: ${widgets.commandButton("System: Reload")}

### Step 2. Save Library/PanelDragResize.js using this button: ${widgets.commandButton("Save: HierarchyHighlightHeadings.js")}

### Step 3. System Reload: ${widgets.commandButton("System: Reload")}

### Step 4. Reload UI: ${widgets.commandButton("Client: Reload UI")}

1. borrowed `JS inject` from [[CONFIG/View/Tree/Float]]
2. https://community.silverbullet.md/t/hhh-hierarchyhighlightheadings-theme/3467

```space-lua
local jsCode = [[
const STATE_KEY = "__xhHighlightState_v2";

function getLevel(el) {
  for (let i = 1; i <= 6; i++) {
    if (el.classList && el.classList.contains(`sb-line-h${i}`)) return i;
  }
  const tag = el.tagName ? el.tagName.toLowerCase() : "";
  if (/^h[1-6]$/.test(tag)) return Number(tag[1]);
  return 0;
}

function pickGroupRoot(start, container, groupSelector) {
  if (!groupSelector) return container;
  const g = start.closest(groupSelector);
  return g || container;
}

function listHeadings(root, headingSelector) {
  return Array.from(root.querySelectorAll(headingSelector));
}

function collectDescendants(startIndex, headings, startLevel) {
  const res = [];
  for (let i = startIndex + 1; i < headings.length; i++) {
    const lvl = getLevel(headings[i]);
    if (lvl <= startLevel) break;
    res.push(headings[i]);
  }
  return res;
}

function collectAncestors(startIndex, headings, startLevel) {
  const res = [];
  let minLevel = startLevel;
  for (let i = startIndex - 1; i >= 0; i--) {
    const lvl = getLevel(headings[i]);
    if (lvl < minLevel) {
      res.push(headings[i]);
      minLevel = lvl;
      if (minLevel === 1) break;
    }
  }
  return res;
}

function clearClasses(root) {
  root.querySelectorAll(".sb-active, .sb-active-anc, .sb-active-desc, .sb-active-current")
      .forEach(el => el.classList.remove("sb-active", "sb-active-anc", "sb-active-desc", "sb-active-current"));
}

export function enableHighlight(opts = {}) {
  const containerSelector = opts.containerSelector || "#sb-main";
  const headingSelector = opts.headingSelector ||
    "h1, h2, h3, h4, h5, h6, .sb-line-h1, .sb-line-h2, .sb-line-h3, .sb-line-h4, .sb-line-h5, .sb-line-h6";
  const groupSelector = opts.groupSelector || ".sb-title-group";
  const debug = !!opts.debug;

  const bind = () => {
    const container = document.querySelector(containerSelector);
    if (!container) { requestAnimationFrame(bind); return; }

    const prev = window[STATE_KEY];
    if (prev && prev.cleanup) prev.cleanup();

    function onPointerOver(e) {
      const h = e.target && e.target.closest && e.target.closest(headingSelector);
      if (!h || !container.contains(h)) return;

      const groupRoot = pickGroupRoot(h, container, groupSelector);
      const headings = listHeadings(groupRoot, headingSelector);
      const startIndex = headings.indexOf(h);
      if (startIndex === -1) return;

      clearClasses(container);

      const startLevel = getLevel(h);
      const descendants = collectDescendants(startIndex, headings, startLevel);
      const ancestors = collectAncestors(startIndex, headings, startLevel);

      h.classList.add("sb-active", "sb-active-current");
      descendants.forEach(el => el.classList.add("sb-active", "sb-active-desc"));
      ancestors.forEach(el => el.classList.add("sb-active", "sb-active-anc"));

      if (debug) {
        console.log(
          "[HHH] level", startLevel,
          "anc", ancestors.length,
          "desc", descendants.length,
          "text:", (h.textContent || "").trim().slice(0, 60)
        );
      }
    }

    function onPointerOut(e) {
      const from = e.target && e.target.closest && e.target.closest(headingSelector);
      const to = e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest(headingSelector);
      if (from && (!to || !container.contains(to))) {
        clearClasses(container);
      }
    }

    function onPointerLeave() {
      clearClasses(container);
    }

    container.addEventListener("pointerover", onPointerOver);
    container.addEventListener("pointerout", onPointerOut);
    container.addEventListener("pointerleave", onPointerLeave);

    const mo = new MutationObserver(() => { clearClasses(container); });
    mo.observe(container, { childList: true, subtree: true });

    window[STATE_KEY] = {
      cleanup() {
        try {
          container.removeEventListener("pointerover", onPointerOver);
          container.removeEventListener("pointerout", onPointerOut);
          container.removeEventListener("pointerleave", onPointerLeave);
        } catch {}
        try { mo.disconnect(); } catch {}
        clearClasses(container);
      }
    };

    if (debug) console.log("[HHH] enabled");
  };

  bind();
}

export function disableHighlight() {
  const st = window[STATE_KEY];
  if (st && st.cleanup) st.cleanup();
  window[STATE_KEY] = null;
}
]]

command.define {
  name = "Save: HierarchyHighlightHeadings.js",
  hide = true,
  run = function()
    local jsFile = space.writeDocument("Library/HierarchyHighlightHeadings.js", jsCode)
    editor.flashNotification("HierarchyHighlightHeadings JS saved with size: " .. jsFile.size .. " bytes")
  end
}
```

```space-lua
command.define {
  name = "Enable: HierarchyHighlightHeadings",
  run = function()
    js.import("/.fs/Library/HierarchyHighlightHeadings.js").enableHighlight()
  end
}

command.define {
  name = "Disable HierarchyHighlightHeadings",
  hide = true,
  run = function()
    js.import("/.fs/Library/HierarchyHighlightHeadings.js").disableHighlight()
  end
}
```

1. borrowed `event.listen` from [[CONFIG/Edit/Read Only Toggle]]

```space-lua
event.listen {
  name = 'system:ready',
  run = function(e)
    js.import("/.fs/Library/HierarchyHighlightHeadings.js").enableHighlight()
  end
}
```

## CSS part

1. Remember to Cancel the `1st space-style block` from [[STYLE/Theme/HHH-css]]

```space-style
/* 默认半透明 */
.sb-line-h1, .sb-line-h2, .sb-line-h3,
.sb-line-h4, .sb-line-h5, .sb-line-h6 {
  opacity: var(--title-opacity);
  /* transition: opacity 0.2s; */
}

/* 标题自身 hover 可高亮该标题 */
.sb-line-h1:hover,
.sb-line-h2:hover,
.sb-line-h3:hover,
.sb-line-h4:hover,
.sb-line-h5:hover,
.sb-line-h6:hover {
  opacity: 1 !important;
}

/* 仅保留 JS 驱动的高亮 */
.sb-active {
  opacity: 1 !important;
}
```

1. https://chatgpt.com/share/68fd0e6f-19d8-8010-95b8-c0f80a829e9b

```space-style
:root {
  /* 🌑 Dark theme - version plus flashy */
  --h1-color-dark: #ff4dff; /* violet électrique */
  --h2-color-dark: #7b68ee; /* bleu-violet vif */
  --h3-color-dark: #1e90ff; /* bleu clair néon */
  --h4-color-dark: #00ff7f; /* vert menthe fluo */
  --h5-color-dark: #ffff33; /* jaune vif */
  --h6-color-dark: #ff8000; /* orange saturé */

  --h1-underline-dark: rgba(255,77,255,0.5);
  --h2-underline-dark: rgba(123,104,238,0.5);
  --h3-underline-dark: rgba(30,144,255,0.5);
  --h4-underline-dark: rgba(0,255,127,0.5);
  --h5-underline-dark: rgba(255,255,51,0.5);
  --h6-underline-dark: rgba(255,128,0,0.5);

  /* ☀️ Light theme - version plus flashy */
  --h1-color-light: #a020f0; /* violet pur */
  --h2-color-light: #0077ff; /* bleu saturé */
  --h3-color-light: #00cc66; /* vert intense */
  --h4-color-light: #ffb700; /* or lumineux */
  --h5-color-light: #ff4500; /* orange rouge vif */
  --h6-color-light: #cc00cc; /* magenta néon */

  --h1-underline-light: rgba(160,32,240,0.5);
  --h2-underline-light: rgba(0,119,255,0.5);
  --h3-underline-light: rgba(0,204,102,0.5);
  --h4-underline-light: rgba(255,183,0,0.5);
  --h5-underline-light: rgba(255,69,0,0.5);
  --h6-underline-light: rgba(204,0,204,0.5);

  --title-opacity: 0.9;
}


/* 公共 H1–H6 样式 */
.sb-line-h1, .sb-line-h2, .sb-line-h3,
.sb-line-h4, .sb-line-h5, .sb-line-h6 {
  position: relative;
  opacity: var(--title-opacity);
  border-bottom-style: solid;
  border-bottom-width: 2px;
  border-image-slice: 1;
}

/* Dark Theme */
html[data-theme="dark"] {
  .sb-line-h1 { font-size:1.8em !important; color:var(--h1-color-dark)!important; border-bottom: 2px solid var(--h1-underline-dark); }
  .sb-line-h2 { font-size:1.6em !important; color:var(--h2-color-dark)!important; border-bottom: 2px solid var(--h2-underline-dark); }
  .sb-line-h3 { font-size:1.4em !important; color:var(--h3-color-dark)!important; border-bottom: 2px solid var(--h3-underline-dark); }
  .sb-line-h4 { font-size:1.2em !important; color:var(--h4-color-dark)!important; border-bottom: 2px solid var(--h4-underline-dark); }
  .sb-line-h5 { font-size:1em !important; color:var(--h5-color-dark)!important; border-bottom: 2px solid var(--h5-underline-dark); }
  .sb-line-h6 { font-size:1em !important; color:var(--h6-color-dark)!important; border-bottom: 2px solid var(--h6-underline-dark); }
}

/* Light Theme */
html[data-theme="light"] {
  .sb-line-h1 { font-size:1.8em !important; color:var(--h1-color-light)!important; border-bottom: 2px solid var(--h1-underline-light); }
  .sb-line-h2 { font-size:1.6em !important; color:var(--h2-color-light)!important; border-bottom: 2px solid var(--h2-underline-light); }
  .sb-line-h3 { font-size:1.4em !important; color:var(--h3-color-light)!important; border-bottom: 2px solid var(--h3-underline-light); }
  .sb-line-h4 { font-size:1.2em !important; color:var(--h4-color-light)!important; border-bottom: 2px solid var(--h4-underline-light); }
  .sb-line-h5 { font-size:1em !important; color:var(--h5-color-light)!important; border-bottom: 2px solid var(--h5-underline-light); }
  .sb-line-h6 { font-size:1em !important; color:var(--h6-color-light)!important; border-bottom: 2px solid var(--h6-underline-light); }
}

/* 高亮类 */
.sb-active {
  opacity: 1 !important;
}
```

```space-style

:root {
  --h-bg-alpha-dark: 20%;   /* 深色主题 */
  --h-bg-alpha-light: 8%;  /* 浅色主题 */
}

/* 深色主题：hover 或 .sb-active 才上很淡背景 */
html[data-theme="dark"] .sb-line-h1:hover,
html[data-theme="dark"] .sb-line-h2:hover,
html[data-theme="dark"] .sb-line-h3:hover,
html[data-theme="dark"] .sb-line-h4:hover,
html[data-theme="dark"] .sb-line-h5:hover,
html[data-theme="dark"] .sb-line-h6:hover,
html[data-theme="dark"] .sb-active {
  background-color: color-mix(in srgb, currentColor var(--h-bg-alpha-dark), transparent);
}

/* 浅色主题：hover 或 .sb-active 才上很淡背景 */
html[data-theme="light"] .sb-line-h1:hover,
html[data-theme="light"] .sb-line-h2:hover,
html[data-theme="light"] .sb-line-h3:hover,
html[data-theme="light"] .sb-line-h4:hover,
html[data-theme="light"] .sb-line-h5:hover,
html[data-theme="light"] .sb-line-h6:hover,
html[data-theme="light"] .sb-active {
  background-color: color-mix(in srgb, currentColor var(--h-bg-alpha-light), transparent);
}

/* 深色：只在 hover 或 sb-active 时给标题行一个很淡的同色背景 */
html[data-theme="dark"] :is(.sb-line-h1,.sb-line-h2,.sb-line-h3,.sb-line-h4,.sb-line-h5,.sb-line-h6):is(:hover,.sb-active) {
  background-color: color-mix(in srgb, currentColor var(--h-bg-alpha-dark), transparent);
}

/* 浅色：同理 */
html[data-theme="light"] :is(.sb-line-h1,.sb-line-h2,.sb-line-h3,.sb-line-h4,.sb-line-h5,.sb-line-h6):is(:hover,.sb-active) {
  background-color: color-mix(in srgb, currentColor var(--h-bg-alpha-light), transparent);
}
```