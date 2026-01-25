---
author: malys
description: Automatically formats Markdown table cells based on hashtag column tags.
tags: userscript
name: "Library/Malys/MdTableRender"
---
# Md table column rendering
This script enhances Markdown tables inside SilverBullet by applying dynamic formatting rules to columns marked with hashtag-style format tags (e.g. `#euro`, `#percent`, `#stars`).
It observes table changes in real time and transforms raw text values into styled, formatted elements — such as currency, percentages, booleans, dates, badges, emojis, trends, and star ratings — without altering the original Markdown source. It is designed to be non-intrusive, editable-friendly, and resilient thanks to mutation observers, debouncing, and a polling fallback.

## Disclaimer & Contributions

This code is provided **as-is**, **without any kind of support or warranty**.  
I do **not** provide user support, bug-fixing on demand, or feature development.

If you detect a bug, please **actively participate in debugging it** (analysis, proposed fix, or pull request) **before reporting it**. Bug reports without investigation may be ignored.

🚫 **No new features will be added.**  
✅ **All types of contributions are welcome**, including bug fixes, refactoring, documentation improvements, and optimizations.

By using or contributing to this project, you acknowledge and accept these conditions.

## Supported renderers (via `#tag` in header)

| Tag | Effect |
|-----|--------|
| **#euro** | Formats number as “12 345 €” |
| **#usd** | Formats number as “$12,345” |
| **#percent** | Converts decimal to percentage (0.15 → “15 %”) |
| **#km** | Formats number as “12 345 km” |
| **#kg** | Formats number as “12 345 kg” |
| **#watt** | Formats number as “12 345 W” |
| **#int** | Parses and formats whole numbers with locale separators |
| **#float** | Forces 2 decimal places (e.g. “3.14”) |
| **#upper** | Forces uppercase |
| **#lower** | Forces lowercase |
| **#bold** | Wraps value in `<strong>` |
| **#italic** | Wraps value in `<em>` |
| **#link** | Turns URL into clickable link |
| **#date** | Formats dates (YYYY-MM-DD or ISO) |
| **#datetime** | Formats full timestamp |
| **#logical** | Converts truthy → `✅` / falsy → `❌` |
| **#stars** | Converts number to up to 10 ⭐ stars |
| **#evaluation** | Converts 0–5 into ★/☆ rating |
| **#badge** | Renders value as a blue pill badge |
| **#emoji** | Converts words like “happy”, “cool”, “neutral” → 😃 😎 😐 |
| **#mood** | Converts evaluation of mood  to emoj 1:bad 5: very well|
| **#trend** | Converts + / - / = into 🔼 🔽 ➡️ |
| **#histo** | Converts number to █ |

Just add the renderer as a hashtag tag in your table header:

```md
| Product   #wine    | Euro #euro| Percent #percent | Logical #logical | Stars #stars| Evaluation #evaluation | Updated            | Mood #emoji  | Trend #trend |
|-------------|------|---------|---------|-------|------------|---------------------|--------|-------|
| Widget      | 12.99| 0.15    | 0       | 3     | 4          | 2025-11-06T14:30:00Z | happy  | +     |
| Gadget      | 8.50 | 0.23    | false      | 5     | 2          | 2024-12-25T10:00:00Z | neutral| -     |
| Thingamajig | 5.75 | 0.05    | true    | 4     | 5          | 2023-05-10T08:15:00Z | cool   | =     |

```
![](https://community.silverbullet.md/uploads/default/original/2X/e/e2598b9faf8fb223eb5b68b9d03b0729384c5351.png)
![](https://community.silverbullet.md/uploads/default/original/2X/e/ec9b8a44f48b1854b94544da609e24fb1c9bf888.gif)
## Code
```space-lua
-- Table Renderer (Formatter)

local cfg = config.get("tableRenderer") or {}
local enabled = cfg.enabled ~= false

--------------------------------------------------
-- CLEANUP
--------------------------------------------------

local function cleanupRenderer()
  local scriptId = "sb-table-renderer-runtime"
  local existing = js.window.document.getElementById(scriptId)

  if existing then
    local ev = js.window.document.createEvent("Event")
    ev.initEvent("sb-table-renderer-unload", true, true)
    js.window.dispatchEvent(ev)
    existing.remove()
    print("Table Renderer: Disabled")
  else
    print("Table Renderer: Already inactive")
  end
end

--------------------------------------------------
-- ENABLE
--------------------------------------------------

function enableTableRenderer()
  local scriptId = "sb-table-renderer-runtime"
  if js.window.document.getElementById(scriptId) then
    print("Table Renderer: Already active")
    return
  end

  local scriptEl = js.window.document.createElement("script")
  scriptEl.id = scriptId

  scriptEl.innerHTML = [[
(function () {
  'use strict';

  const DEBUG = false;
  const log = (...a) => DEBUG && console.log('[sb-table-renderer]', ...a);

  /* ---------------- FORMATTERS ---------------- */

  const formatters = {
    euro: v => isNaN(v) ? v : `${parseFloat(v).toLocaleString()} €`,
    usd: v => isNaN(v) ? v : `$${parseFloat(v).toLocaleString()}`,
    kg: v => isNaN(v) ? v : `${parseFloat(v).toLocaleString()} kg`,
    km: v => isNaN(v) ? v : `${parseFloat(v).toLocaleString()} km`,
    watt: v => isNaN(v) ? v : `${parseFloat(v).toLocaleString()} W`,
    percent: v => isNaN(v) ? v : `${(parseFloat(v) * 100).toFixed(0)} %`,
    int: v => isNaN(v) ? v : parseInt(v, 10).toLocaleString(),
    float: v => isNaN(v) ? v : parseFloat(v).toFixed(2),
    upper: v => v.toString().toUpperCase(),
    lower: v => v.toString().toLowerCase(),
    bold: v => `<strong>${v}</strong>`,
    italic: v => `<em>${v}</em>`,
    link: v => `<a href="${v}" target="_blank">${v.replace(/^https?:\/\//, '')}</a>`,
    date: v => formatDate(v),
    datetime: v => formatDateTime(v),
    logical: v => {
      if(v !=='✅' &&  v !=='❌'){
        const val = v.toString().toLowerCase().trim();
        return (val === '1' || val === 'true' || val === 'yes' || val === 'ok') ? '✅' : '❌';
      }
      return v;
    },
    stars: v => {
      const n = parseInt(v, 10);
      return isNaN(n) ? v : '⭐'.repeat(Math.max(0, Math.min(n, 10)));
    },
    evaluation: v => {
      const n = parseInt(v, 10);
      if (isNaN(n)) return v;
      return '★'.repeat(Math.max(0, Math.min(n, 5))) + '☆'.repeat(5 - Math.max(0, Math.min(n, 5)));
    },
    histo: v => {
      const n = parseInt(v, 10);
      return isNaN(n) ? v : '█'.repeat(n);
    },
    badge: v => `<span style="background:#2196f3;color:white;padding:2px 6px;border-radius:8px;font-size:0.9em;">${v}</span>`,
    mood: v => {
      const n = parseInt(v, 10);
      const moodScaleSoft = ['😔', '🙁', '😐', '🙂', '😄'];
      return moodScaleSoft[(n-1)%5]
    },
    emoji: v => {
        const map = {
        // basic emotions
        happy: '😃',
        sad: '😢',
        angry: '😠',
        love: '❤️',
        neutral: '😐',
        cool: '😎',
        
        
        // positive / joyful
        smile: '😊',
        grin: '😁',
        laugh: '😂',
        excited: '🤩',
        proud: '😌',
        relieved: '😮‍💨',
        thankful: '🙏',
        party: '🥳',
        confident: '😏',
        
        
        // negative / difficult
        cry: '😭',
        disappointed: '😞',
        worried: '😟',
        anxious: '😰',
        scared: '😱',
        tired: '😴',
        sick: '🤒',
        bored: '😒',
        frustrated: '😤',
        confused: '😕',
        
        
        // reactions
        surprised: '😮',
        shocked: '😲',
        thinking: '🤔',
        facepalm: '🤦',
        shrug: '🤷',
        eyeRoll: '🙄',
        
        
        // social / playful
        wink: '😉',
        kiss: '😘',
        hug: '🤗',
        teasing: '😜',
        silly: '🤪',
        
        
        // approval / disapproval
        ok: '👌',
        thumbsUp: '👍',
        thumbsDown: '👎',
        clap: '👏',
        respect: '🫡',
        
        
        // status / misc
        fire: '🔥',
        star: '⭐',
        check: '✅',
        cross: '❌',
        warning: '⚠️',
        };
      const key = v.toString().toLowerCase();
      return map[key] || v;
    },
    trend: v => {
      const val = v.trim();
      if (val === '+') return '🔼';
      if (val === '-') return '🔽';
      if (val === '=') return '➡️';
      return val;
    },
  };

  /* ---------------- CORE ---------------- */

  function extractFormats(table) {
    const formats = [];
    const header =
      table.querySelector('thead tr') ||
      table.querySelector('tr');
    if (!header) return formats;

    [...header.cells].forEach((cell, idx) => {
      formats[idx] = null;
      const tags = cell.querySelectorAll('a.hashtag,[data-tag-name]');
      for (const tag of tags) {
        const name =
          tag.dataset?.tagName ||
          tag.textContent?.replace('#','');
        if (formatters[name]) {
          formats[idx] = name;
          tag.style.display = 'none';
          break;
        }
      }
    });
    return formats;
  }

  function processTable(table) {
    if (table.dataset.sbFormatted) return;
    const formats = extractFormats(table);
    const rows = table.tBodies[0]?.rows || [];

    [...rows].forEach(row => {
      [...row.cells].forEach((cell, idx) => {
        const fmt = formats[idx];
        if (!fmt) return;

        const raw = cell.textContent.trim();
        const out = formatters[fmt](raw);
        if (out !== raw) {
          cell.textContent = out;
          cell.dataset.sbformatted = fmt;
        }
      });
    });

    table.dataset.sbFormatted = 'true';
  }

  function scan() {
    document
      .querySelectorAll('#sb-editor table')
      .forEach(processTable);
  }

  /* ---------------- OBSERVER ---------------- */

  const observer = new MutationObserver(scan);
  observer.observe(document.body, { childList:true, subtree:true });

  scan();

  /* ---------------- CLEANUP ---------------- */

  window.addEventListener('sb-table-renderer-unload', function cln() {
    observer.disconnect();
    document
      .querySelectorAll('[data-sbformatted]')
      .forEach(c => {
        c.removeAttribute('data-sbformatted');
      });
    document
      .querySelectorAll('table[data-sb-formatted]')
      .forEach(t => delete t.dataset.sbFormatted);
    window.removeEventListener('sb-table-renderer-unload', cln);
  });

})();
  ]]

  js.window.document.body.appendChild(scriptEl)
end

--------------------------------------------------
-- COMMANDS
--------------------------------------------------

command.define {
  name = "Table: Enable Renderer",
  run = function() enableTableRenderer() end
}

command.define {
  name = "Table: Disable Renderer",
  run = function() cleanupRenderer() end
}

--------------------------------------------------
-- AUTOSTART
--------------------------------------------------
if enabled then
  enableTableRenderer()
else
  cleanupRenderer()
end
```

## Changelog

* 2026-01-24:
  * feat: convert to space-lua
  * feat: add renderers (mood, emoj)
* 2026-01-02 feat: add kg, km, watt, histo

## Community

[Silverbullet forum](https://community.silverbullet.md/t/md-table-renderers/3545/15)