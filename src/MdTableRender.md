---
author: malys
description: Automatically formats Markdown table cells based on hashtag column tags.
tags: userscript
name: "Library/Malys/MdTableRender"
---
# Md table column rendering

This script enhances Markdown tables inside SilverBullet by applying dynamic
formatting rules to columns marked with hashtag-style format tags (e.g. `#euro`,
`#percent`, `#stars`). It observes table changes in real time and transforms raw
text values into styled, formatted elements — such as currency, percentages,
booleans, dates, badges, emojis, trends, and star ratings — without altering the
original Markdown source. It is designed to be non-intrusive, editable-friendly,
and resilient thanks to mutation observers, debouncing, and a polling fallback.

## Disclaimer & Contributions

This code is provided **as-is**, **without any kind of support or warranty**.  
I do **not** provide user support, bug-fixing on demand, or feature development.

If you detect a bug, please **actively participate in debugging it** (analysis,
proposed fix, or pull request) **before reporting it**. Bug reports without
investigation may be ignored.

🚫 **No new features will be added.**  
✅ **All types of contributions are welcome**, including bug fixes, refactoring,
documentation improvements, and optimizations.

By using or contributing to this project, you acknowledge and accept these
conditions.

## Supported renderers (via `#tag` in header)

| Tag             | Effect                                                    |
| --------------- | --------------------------------------------------------- |
| **#euro**       | Formats number as “12 345 €”                              |
| **#usd**        | Formats number as “$12,345”                               |
| **#percent**    | Converts decimal to percentage (0.15 → “15 %”)            |
| **#gauge**      | Graphical percentage representation ███░                  |
| **#posneg**     | Colored gauge -2 🟥🟥,0 ⬜, +1 🟩                         |
| **#km**         | Formats number as “12 345 km”                             |
| **#kg**         | Formats number as “12 345 kg”                             |
| **#watt**       | Formats number as “12 345 W”                              |
| **#int**        | Parses and formats whole numbers with locale separators   |
| **#float**      | Forces 2 decimal places (e.g. “3.14”)                     |
| **#upper**      | Forces uppercase                                          |
| **#lower**      | Forces lowercase                                          |
| **#bold**       | Wraps value in `<strong>`                                 |
| **#italic**     | Wraps value in `<em>`                                     |
| **#link**       | Turns URL into clickable link                             |
| **#date**       | Formats dates (YYYY-MM-DD or ISO)                         |
| **#datetime**   | Formats full timestamp                                    |
| **#logical**    | Converts truthy → `✅` / falsy → `❌`                     |
| **#stars**      | Converts number to up to 10 ⭐ stars                      |
| **#evaluation** | Converts 0–5 into ★/☆ rating                              |
| **#badge**      | Renders value as a blue pill badge                        |
| **#emoji**      | Converts words like “happy”, “cool”, “neutral” → 😃 😎 😐 |
| **#mood**       | Converts evaluation of mood to emoj 1:bad 5: very well    |
| **#trend**      | Converts + / - / = into 🔼 🔽 ➡️                          |
| **#histo**      | Converts number to █                                      |

Just add the renderer as a hashtag tag in your table header:

```md
| Product #wine | Euro #euro | Percent #percent | Logical #logical | Stars #stars | Evaluation #evaluation | Updated              | Mood #emoji | Trend #trend |
| ------------- | ---------- | ---------------- | ---------------- | ------------ | ---------------------- | -------------------- | ----------- | ------------ |
| Widget        | 12.99      | 0.15             | 0                | 3            | 4                      | 2025-11-06T14:30:00Z | happy       | +            |
| Gadget        | 8.50       | 0.23             | false            | 5            | 2                      | 2024-12-25T10:00:00Z | neutral     | -            |
| Thingamajig   | 5.75       | 0.05             | true             | 4            | 5                      | 2023-05-10T08:15:00Z | cool        | =            |
```

![](https://community.silverbullet.md/uploads/default/original/2X/e/e2598b9faf8fb223eb5b68b9d03b0729384c5351.png)
![](https://community.silverbullet.md/uploads/default/original/2X/e/ec9b8a44f48b1854b94544da609e24fb1c9bf888.gif)
## How to

### Add new renderer

```lua 
mls = mls or {}
mls.table = mls.table or {}
mls.table.renderer = mls.table.renderer or {}

mls.table.renderer["euro"] = {
     	completion = {
			{
				name = "one",
				value = "1"
			},
			{
				name = "two",
				value = "2"
			},
		}, 
		visual = [[isNaN(v) ? v : `${parseFloat(v).toLocaleString()} TEST`]],
		validation = function(v){
          --...
          return true
        }
}
```
## Code

```space-lua


-- Table Renderer (Formatter)
mls = mls or {}
mls.table = mls.table or {}
mls.table.renderer = mls.table.renderer or {}

local cfg = config.get("tableRenderer") or {}
local enabled = cfg.enabled ~= false

--------------------------------------------------
-- FUNCTION
--------------------------------------------------
function mls.table.cleanupRenderer()
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

------------------------------------------------
-- Generic validators
------------------------------------------------

local function isNumber(v)
	return tonumber(v) ~= nil
end

local function isBetween(v, min, max)
	v = tonumber(v)
	return v ~= nil and v >= min and v <= max
end

local function isInt(v)
	v = tonumber(v)
	return v ~= nil and math.floor(v) == v
end

------------------------------------------------
-- Renderers (JS visual + Lua validation)
------------------------------------------------
mls.table.renderer = {
	euro = {
		visual = [[isNaN(v) ? v : `${parseFloat(v).toLocaleString()} €`]],
		validation = isNumber
	},
	usd = {
		visual = [[isNaN(v) ? v : `$${parseFloat(v).toLocaleString()}`]],
		validation = isNumber
	},
	kg = {
		visual = [[isNaN(v) ? v : `${parseFloat(v).toLocaleString()} kg`]],
		validation = isNumber
	},
	km = {
		visual = [[isNaN(v) ? v : `${parseFloat(v).toLocaleString()} km`]],
		validation = isNumber
	},
	watt = {
		visual = [[isNaN(v) ? v : `${parseFloat(v).toLocaleString()} W`]],
		validation = isNumber
	},
	percent = {
		visual = [[isNaN(v) ? v : `${(parseFloat(v) * 100).toFixed(0)} %`]],
		validation = isNumber
	},
	int = {
		visual = [[isNaN(v) ? v : parseInt(v, 10).toLocaleString()]],
		validation = isInt
	},
	float = {
		visual = [[isNaN(v) ? v : parseFloat(v).toFixed(2)]],
		validation = isNumber
	},
	upper = {
		visual = [[v.toString().toUpperCase()]],
		validation = function(v)
			return v ~= nil
		end
	},
	lower = {
		visual = [[v.toString().toLowerCase()]],
		validation = function(v)
			return v ~= nil
		end
	},
	bold = {
		visual = [[`<strong>${v}</strong>`]],
		validation = function(v)
			return v ~= nil
		end
	},
	italic = {
		visual = [[`<em>${v}</em>`]],
		validation = function(v)
			return v ~= nil
		end
	},
	link = {
		visual = [[`<a href="${v}" target="_blank">${v.replace(/^https?:\/\//, '')}</a>`]],
		validation = function(v)
			return type(v) == "string" and v:match("^https?://")
		end
	},
	logical = {
		completion = {
			{
				name = "❌",
				value = "false"
			},
			{
				name = "✅",
				value = "true"
			},
		},
		visual = [[
      if (v !== '✅' && v !== '❌') {
        const val = v.toString().toLowerCase().trim();
        return (val === '1' || val === 'true' || val === 'yes' || val === 'ok') ? '✅' : '❌';
      }
      return v;
    ]],
		validation = function(v)
			return v ~= nil
		end
	},
	evaluation = {
		completion = {
			{
				name = "🤍🤍🤍🤍🤍",
				value = "0"
			},
			{
				name = "❤️🤍🤍🤍🤍",
				value = "1"
			},
			{
				name = "❤️❤️🤍🤍🤍",
				value = "2"
			},
			{
				name = "❤️❤️❤️🤍🤍",
				value = "3"
			},
			{
				name = "❤️❤️❤️❤️🤍",
				value = "4"
			},
			{
				name = "❤️❤️❤️❤️❤️",
				value = "5"
			},
		},
		visual = [[
      const n = parseInt(v, 10);
      if (isNaN(n)) return v;
      return '❤️'.repeat(Math.max(0, Math.min(n, 5)))
           + '🤍'.repeat(5 - Math.max(0, Math.min(n, 5)));
    ]],
		validation = function(v)
			return isBetween(v, 1, 5)
		end
	},
	histo = {
		visual = [[
      const n = parseInt(v, 10);
      return isNaN(n) ? v : '█'.repeat(n);
    ]],
		validation = isInt
	},
	gauge = {
		visual = [[
      const a = 0;
      const b = 100;
      const val = parseInt(v, 10);
      if (isNaN(val)) return v;
      const clampedValue = Math.max(a, Math.min(val, b));
      const percentage = (clampedValue - a) / (b - a);
      const filled = Math.floor(percentage * 10);
      const empty = 10 - filled;
      return `[${'█'.repeat(filled)}${'░'.repeat(empty)}]`;
    ]],
		validation = function(v)
			return isBetween(v, 0, 100)
		end
	},
	trend = {
		completion = {
			{
				name = "🔼",
				value = "+"
			},
			{
				name = "🔽",
				value = "-"
			},
			{
				name = "➡️",
				value = "="
			}
		},
		visual = [[
      const val = v.trim();
      if (val === '+') return '🔼';
      if (val === '-') return '🔽';
      if (val === '=') return '➡️';
      return val;
    ]],
		validation = function(v)
			return v == "+" or v == "-" or v == "="
		end
	},
	emoji = {
		completion = {
  -- basic emotions
			{
				name = "happy 😃",
				value = "happy"
			},
			{
				name = "sad 😢",
				value = "sad"
			},
			{
				name = "angry 😠",
				value = "angry"
			},
			{
				name = "love ❤️",
				value = "love"
			},
			{
				name = "neutral 😐",
				value = "neutral"
			},
			{
				name = "cool 😎",
				value = "cool"
			},

  -- positive / joyful
			{
				name = "smile 😊",
				value = "smile"
			},
			{
				name = "grin 😁",
				value = "grin"
			},
			{
				name = "laugh 😂",
				value = "laugh"
			},
			{
				name = "excited 🤩",
				value = "excited"
			},
			{
				name = "proud 😌",
				value = "proud"
			},
			{
				name = "relieved 😮‍💨",
				value = "relieved"
			},
			{
				name = "thankful 🙏",
				value = "thankful"
			},
			{
				name = "party 🥳",
				value = "party"
			},
			{
				name = "confident 😏",
				value = "confident"
			},

  -- negative / difficult
			{
				name = "cry 😭",
				value = "cry"
			},
			{
				name = "disappointed 😞",
				value = "disappointed"
			},
			{
				name = "worried 😟",
				value = "worried"
			},
			{
				name = "anxious 😰",
				value = "anxious"
			},
			{
				name = "scared 😱",
				value = "scared"
			},
			{
				name = "tired 😴",
				value = "tired"
			},
			{
				name = "sick 🤒",
				value = "sick"
			},
			{
				name = "bored 😒",
				value = "bored"
			},
			{
				name = "frustrated 😤",
				value = "frustrated"
			},
			{
				name = "confused 😕",
				value = "confused"
			},

  -- reactions
			{
				name = "surprised 😮",
				value = "surprised"
			},
			{
				name = "shocked 😲",
				value = "shocked"
			},
			{
				name = "thinking 🤔",
				value = "thinking"
			},
			{
				name = "facepalm 🤦",
				value = "facepalm"
			},
			{
				name = "shrug 🤷",
				value = "shrug"
			},
			{
				name = "eyeRoll 🙄",
				value = "eyeroll"
			},

  -- social / playful
			{
				name = "wink 😉",
				value = "wink"
			},
			{
				name = "kiss 😘",
				value = "kiss"
			},
			{
				name = "hug 🤗",
				value = "hug"
			},
			{
				name = "teasing 😜",
				value = "teasing"
			},
			{
				name = "silly 🤪",
				value = "silly"
			},

  -- approval / disapproval
			{
				name = "ok 👌",
				value = "ok"
			},
			{
				name = "thumbsUp 👍",
				value = "thumbsup"
			},
			{
				name = "thumbsDown 👎",
				value = "thumbsdown"
			},
			{
				name = "clap 👏",
				value = "clap"
			},
			{
				name = "respect 🫡",
				value = "respect"
			},

  -- status / misc
			{
				name = "fire 🔥",
				value = "fire"
			},
			{
				name = "star ⭐",
				value = "star"
			},
			{
				name = "check ✅",
				value = "check"
			},
			{
				name = "cross ❌",
				value = "cross"
			},
			{
				name = "warning ⚠️",
				value = "warning"
			},
		},
		visual = [[
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
    ]],
		validation = function(v)
			return type(v) == "string"
		end
	},
	posneg = {
		completion = {
			{
				name = "-2 🟥🟥",
				value = "-2"
			},
			{
				name = "-1 🟥",
				value = "-1"
			},
			{
				name = "0 ⬜",
				value = "2"
			},
			{
				name = "1 🟩",
				value = "1"
			},
			{
				name = "2 🟩🟩",
				value = "2"
			},
		},
		visual = [[
      if (isNaN(v)) return v;
      const val = parseInt(v, 10);
      if (val < 0) return "🟥".repeat(Math.abs(val));
      if (val > 0) return "🟩".repeat(Math.abs(val));
      return "⬜";
    ]],
		validation = function(v)
			return isBetween(v, -10, 10)
		end
	},
	speed = {
		visual = [[v + " km/h"]],
		validation = function(v)
			return isBetween(v, 0, 300)
		end
	},
	mood = {
		completion = {
			{
				name = "😞",
				value = "1"
			},
			{
				name = "🙁",
				value = "2"
			},
			{
				name = "😐",
				value = "3"
			},
			{
				name = "🙂",
				value = "4"
			},
			{
				name = "😄",
				value = "5"
			},
		},
		visual = [[
    const n = parseInt(v, 10);
    const moodScaleSoft = ['😔', '🙁', '😐', '🙂', '😄'];
    return moodScaleSoft[(n - 1) % 5];
  ]],
		validation = function(v)
			return isBetween(v, 1, 5)
		end
	},
	stars = {
		completion = {
			{
				name = "1 ⭐",
				value = "1"
			},
			{
				name = "2 ⭐⭐",
				value = "2"
			},
			{
				name = "3 ⭐⭐⭐",
				value = "3"
			},
			{
				name = "4 ⭐⭐⭐⭐",
				value = "4"
			},
			{
				name = "5 ⭐⭐⭐⭐⭐",
				value = "5"
			},
			{
				name = "6 ⭐⭐⭐⭐⭐⭐",
				value = "6"
			},
			{
				name = "7 ⭐⭐⭐⭐⭐⭐⭐",
				value = "7"
			},
			{
				name = "8 ⭐⭐⭐⭐⭐⭐⭐⭐",
				value = "8"
			},
			{
				name = "9 ⭐⭐⭐⭐⭐⭐⭐⭐⭐",
				value = "9"
			},
			{
				name = "10 ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐",
				value = "10"
			},
		},
		visual = [[
    const n = parseInt(v, 10);
    return isNaN(n) ? v : '⭐'.repeat(Math.max(0, Math.min(n, 10)));
  ]],
		validation = function(v)
			return isBetween(v, 1, 10)
		end
	},
	badge = {
		completion = {},
		visual = [[
    return `<span style="background:#2196f3;color:white;padding:2px 6px;border-radius:8px;font-size:0.9em;">${v}</span>`;
  ]],
		validation = function(v)
			return v ~= nil
		end
	},
}

------------------------------------------------
-- Dispatcher
------------------------------------------------
mls.table.render = function(label, rendererN)
	local rendererName = rendererN
	if (type(rendererN) == "table") then
		for _, tag in ipairs(rendererN) do
			if mls.table.renderer[tag] then
				rendererName = tag
			end
		end
	end
	if label and rendererName and mls.table.renderer[rendererName] then
		local renderer = mls.table.renderer[rendererName]
		local input
		if renderer.completion and # renderer.completion > 0 then
			input = editor.filterBox(label, renderer.completion)
		else
			input = editor.prompt(label)
		end
		local value = input
		if input and input.value then
			value = input.value
		end
		if renderer.validation(value) then
			return value
		else
			editor.flashNotification("Input not valid: " .. tostring(input), "error")
		end
	else
		editor.flashNotification("Missing renderer: " .. tostring(rendererName), "error")
	end
end

------------------------------------------------
-- JS generator
------------------------------------------------
local function exportJSFormatters(renderers)
	local lines = {}
	table.insert(lines, "const formatters = {")
	for name, def in pairs(renderers) do
		if def.visual then
			local js = def.visual
      -- single line or block
			if string.match(js, "\n") then
				table.insert(lines, "  " .. name .. ": v => {")
				table.insert(lines, js)
				table.insert(lines, "  },")
			else
				table.insert(lines, "  " .. name .. ": v => " .. js .. ",")
			end
		end
	end
	table.insert(lines, "};")
	return table.concat(lines, "\n")
end

--------------------------------------------------
-- ENABLE
--------------------------------------------------

function mls.table.enableTableRenderer()
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
]] .. exportJSFormatters(mls.table.renderer) .. [[
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
          tag.textContent?.replace('#', '');
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
  observer.observe(document.body, { childList: true, subtree: true });

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

})()
  ]]
	js.window.document.body.appendChild(scriptEl)
end

--------------------------------------------------
-- COMMANDS
--------------------------------------------------

command.define{
	name = "Table: Enable Renderer",
	run = function()
		mls.table.enableTableRenderer()
	end
}

command.define{
	name = "Table: Disable Renderer",
	run = function()
		mls.table.cleanupRenderer()
	end
}
--------------------------------------------------
-- AUTOSTART
--------------------------------------------------
if enabled then
	mls.table.enableTableRenderer()
else
	mls.table.cleanupRenderer()
end
```

## Changelog
- 2026-02-01
  - feat: define renderers in lua
  - feat: add validation mechanism
  - feat: add completion mechanism
- 2026-01-24:
    - feat: convert to space-lua
    - feat: add renderers (mood, emoj)
- 2026-01-02 feat: add kg, km, watt, histo

## Community

[Silverbullet forum](https://community.silverbullet.md/t/md-table-renderers/3545/15)

