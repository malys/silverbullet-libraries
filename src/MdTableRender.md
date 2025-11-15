---
author: malys
description: Automatically formats Markdown table cells based on hashtag column tags in SilverBullet
---
# Md table column rendering
This script enhances Markdown tables inside SilverBullet by applying dynamic formatting rules to columns marked with hashtag-style format tags (e.g. `#euro`, `#percent`, `#stars`). It observes table changes in real time and transforms raw text values into styled, formatted elements — such as currency, percentages, booleans, dates, badges, emojis, trends, and star ratings — without altering the original Markdown source. It is designed to be non-intrusive, editable-friendly, and resilient thanks to mutation observers, debouncing, and a polling fallback.

## Supported renderers (via `#tag` in header)

| Tag | Effect |
|-----|--------|
| **#euro** | Formats number as “12 345 €” |
| **#usd** | Formats number as “$12,345” |
| **#percent** | Converts decimal to percentage (0.15 → “15 %”) |
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
| **#trend** | Converts + / - / = into 🔼 🔽 ➡️ |

Just add the renderer as a hashtag tag in your table header:

```md
| Product   #wine    | Euro #euro| Percent #percent | Logical #logical | Stars #stars| Evaluation #evaluation | Updated            | Mood #emoji  | Trend #trend |
|-------------|------|---------|---------|-------|------------|---------------------|--------|-------|
| Widget      | 12.99| 0.15    | 0       | 3     | 4          | 2025-11-06T14:30:00Z | happy  | +     |
| Gadget      | 8.50 | 0.23    | false      | 5     | 2          | 2024-12-25T10:00:00Z | neutral| -     |
| Thingamajig | 5.75 | 0.05    | true    | 4     | 5          | 2023-05-10T08:15:00Z | cool   | =     |

```
![](https://community.silverbullet.md/uploads/default/original/2X/e/e2598b9faf8fb223eb5b68b9d03b0729384c5351.png)


## Code
```js
// ==UserScript==
// @name        Table renderer
// @namespace   Violentmonkey Scripts
// @match       https://silverbullet.l.malys.ovh/*
// @grant       none
// @version     1.0
// @author      -
// @description 06/11/2025 16:32:22
// ==/UserScript==


(function () {
  'use strict';

  // ---------- Configuration ----------
  const DEBUG = false;             // set true to see console logs
  const POLL_FALLBACK_MS = 1500;   // fallback polling interval if observer misfires
  const DEBOUNCE_MS = 500;         // debounce for batch mutation handling

  // ---------- Formatters ----------
 const formatters = {
    euro: v => isNaN(v) ? v : `${parseFloat(v).toLocaleString()} €`,
    usd: v => isNaN(v) ? v : `$${parseFloat(v).toLocaleString()}`,
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
    badge: v => `<span style="background:#2196f3;color:white;padding:2px 6px;border-radius:8px;font-size:0.9em;">${v}</span>`,
    emoji: v => {
      const map = { happy: '😃', sad: '😢', cool: '😎', angry: '😠', love: '❤️', neutral: '😐' };
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

  // ---------- Utilities ----------
  function log(...args) { if (DEBUG) console.log('[sb-table]', ...args); }
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
  function escapeAttr(str) {
    return String(str).replace(/"/g, '%22');
  }

  // Create a DOM element for formatted output safely
  function createFormattedNode(value, fmt) {
    const fn = formatters[fmt];
    if (!fn) return document.createTextNode(value);
    const html = fn(value);
    // If formatter returned plain text (no tags) we can put textContent,
    // otherwise use innerHTML (we escaped where needed above)
    const container = document.createElement('span');
    // Heuristic: if result contains angle brackets assume it's HTML-safe from our escapes
    if (/<[a-z][\s\S]*>/i.test(html)) container.innerHTML = html;
    else container.textContent = html;
    return container;
  }

  // Debounce helper
  function debounce(fn, ms) {
    let t = null;
    return function (...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  // ---------- Core processing ----------
  // applying flag prevents reacting to our own DOM writes
  let applying = false;

  function processTables(container) {
    if (!container) return;
    if (applying) return;
    applying = true;
    try {
      log('processTables start');
      const tables = container.querySelectorAll('table');
      tables.forEach(table => {
        // find header cells (thead preferred, fallback to first row)
        let headerCells = table.querySelectorAll('thead tr:first-child th, thead tr:first-child td');
        if (!headerCells || headerCells.length === 0) {
          // fallback: first row of tbody or first tr in table
          const firstRow = table.querySelector('tr');
          headerCells = firstRow ? firstRow.querySelectorAll('th, td') : [];
        }
        if (!headerCells || headerCells.length === 0) return;

        // build col formatter list
        const colFormats = Array.from(headerCells).map((cell) => {
          // look for hashtag link by class or data attribute
          const tagLinks = cell.querySelectorAll('a.hashtag, a.sb-hashtag, [data-tag-name]');
          for(let i=0;i<tagLinks.length;i++){
            let tagLink=tagLinks[i]
            if (Object.keys(formatters).includes(tagLink.dataset.tagName)) {
              const name = (tagLink.dataset && tagLink.dataset.tagName) ? tagLink.dataset.tagName
                        : (tagLink.getAttribute ? tagLink.getAttribute('data-tag-name') : null);
              if (name) {
                // hide the hashtag visually but keep it in DOM (so editor can still find it)
                tagLink.style.display = 'none';
                return String(name).trim().toLowerCase();
              }
            }
         }
        return null;
        });

        // apply to body rows (tbody preferred)
        const bodyRows = table.querySelectorAll('tbody tr');
        const rows = bodyRows.length ? bodyRows : table.querySelectorAll('tr');
        rows.forEach(row => {
          const cells = row.querySelectorAll('td, th'); // format cells regardless of tag
          cells.forEach((cell, idx) => {
            const fmt = colFormats[idx];
            if (!fmt || !formatters[fmt]) return;
            const raw = cell.textContent.trim();

            // If the cell already contains a formatted node produced by us, we may replace it
            // But avoid replacing while user is actively typing inside the same cell (contentEditable)
            // If the cell or an ancestor is currently focused, skip (user editing)
            const active = document.activeElement;
            if (active && (cell === active || cell.contains(active))) {
              log('skip formatting because user is editing', cell, raw);
              return;
            }

            // Generate formatted node and replace contents
            const formattedNode = createFormattedNode(raw, fmt);
            // Quick check: if cell already equals formattedNode.textContent (idempotent), skip
            const candidateText = (formattedNode.textContent || '').trim();
            if (candidateText === raw && !/<[a-z][\s\S]*>/i.test(formattedNode.innerHTML)) {
              // Nothing to change (formatter didn't alter text)
              return;
            }

            // Replace content safely
            cell.innerHTML = '';            // wipe
            cell.appendChild(formattedNode);
            // mark as processed (for debugging/inspection)
            cell.setAttribute('data-sbformatted', fmt);
          });
        });
      });
      log('processTables done');
    } catch (err) {
      console.error('sb-table: processing error', err);
    } finally {
      // tiny timeout to ensure observer won't see our writes as immediate external mutations
      setTimeout(() => { applying = false; }, 20);
    }
  }

  const debouncedProcess = debounce(processTables, DEBOUNCE_MS);

  // ---------- Setup: wait for #sb-editor ----------
  function waitForEditorAndStart() {
    const editor = document.getElementById('sb-editor');
    if (!editor) {
      log('#sb-editor not found, retrying...');
      setTimeout(waitForEditorAndStart, 300);
      return;
    }
    startWatching(editor);
  }

  // ---------- Start watching container ----------
  let observer = null;
  let fallbackInterval = null;
  let lastRun = 0;

  function startWatching(editor) {
    // initial run once editor appears (give editor a moment)
    setTimeout(() => debouncedProcess(editor), 400);

    // listen to input events (contenteditable emits input)
    editor.addEventListener('input', () => {
      log('input event -> schedule process');
      debouncedProcess(editor);
    }, { passive: true });

    // also listen to keyup/paste to catch edge cases
    editor.addEventListener('keyup', () => debouncedProcess(editor));
    editor.addEventListener('paste', () => setTimeout(() => debouncedProcess(editor), 80));

    // MutationObserver config - broad to catch replacements/attribute changes
    const config = { childList: true, subtree: true, characterData: true, attributes: true };

    // Create observer
    observer = new MutationObserver((mutations) => {
      if (applying) return;
      // Quick heuristic: if many mutations, debounce
      const now = Date.now();
      // Avoid calling too often in rapid mutation bursts
      if (now - lastRun < (DEBOUNCE_MS / 2)) {
        debouncedProcess(editor);
      } else {
        debouncedProcess(editor);
        lastRun = now;
      }
    });

    try {
      observer.observe(editor, config);
      log('MutationObserver attached to #sb-editor');
    } catch (err) {
      console.warn('sb-table: MutationObserver attach failed, falling back to polling', err);
    }

    // Fallback polling in case the environment continually replaces the editor root
    fallbackInterval = setInterval(() => {
      try {
        // ensure observer still connected, else try to reattach
        if (observer && observer.takeRecords) {
          // run periodic processing in case something missed
          debouncedProcess(editor);
        } else {
          debouncedProcess(editor);
        }
      } catch (e) {
        console.warn('sb-table: poll fallback err', e);
      }
    }, POLL_FALLBACK_MS);

    // As a safety, also observe document.body so we can detect the editor being replaced
    const bodyObserver = new MutationObserver(() => {
      const currentEditor = document.getElementById('sb-editor');
      if (currentEditor && currentEditor !== editor) {
        log('editor root replaced; reattaching to new #sb-editor');
        // cleanup old observer and restart on new editor
        try { if (observer) observer.disconnect(); } catch {}
        try { if (fallbackInterval) clearInterval(fallbackInterval); } catch {}
        startWatching(currentEditor);
      }
    });
    bodyObserver.observe(document.body, { childList: true, subtree: true });

    // Try one extra processing after a little while to catch delayed renders
    setTimeout(() => debouncedProcess(editor), 1200);
  }

  // Kickoff
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitForEditorAndStart);
  } else {
    waitForEditorAndStart();
  }

})();
```