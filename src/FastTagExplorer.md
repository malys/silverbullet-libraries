---
author: malys
description: Generate wall of children page tags 
---
# Fast tag explorer

From [community](http://community.silverbullet.md/t/super-fast-tag-page-navigator/2203/10), generate tags of children page

```space-style
.fastnav-tags button {
  background-color: var(--root-background-color);
  color: var(--root-color);
  margin-top: 5px;
  margin-right: -5px;
  padding: 0.3em 0.3em;
  border: none;
  border-radius: 6px;
  font-size: 0.9em;
  font-weight: 500;
  cursor: pointer;
}

.fastnav-tags button:hover {
  background-color: var(--meta-subtle-color);
  color: var(--root-color);
}

.fastnav-tags button.active-tag {
  background-color: var(--editor-hashtag-background-color);
  color: var(--editor-hashtag-color);
}

.fastnav-tags button span.fn-c {
  font-size: 0.7em;
  vertical-align: super;
  opacity: 0.5;
  margin-left: 4px;
}

.fn-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: 10px 0;
  padding: 10px 0;
}

.fn-pagination button {
  background-color: var(--editor-hashtag-background-color);
  color: var(--editor-hashtag-color);
  padding: 0.4em 0.8em;
  border: 1px solid var(--button-border-color);
  border-radius: 6px;
  font-size: 0.9em;
  cursor: pointer;
}

.fn-pagination button:hover:not(:disabled) {
  background-color: var(--meta-subtle-color);
  color: var(--root-color);
}

.fn-pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.fn-page-info {
  font-size: 0.9em;
  color: var(--root-color);
}

.fastnav-pages {
  padding-top: 5px;
  font-size: 0.9em;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.fastnav-pages span {
  background-color: var(--editor-code-background-color);
  border: 1px solid var(--button-border-color);
  flex: 1 1 calc(20% - 8px);
  padding: 0.4em 0.6em;
  text-align: center;
  border-radius: 10px;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.1);
}

.fastnav-pages span:hover {
  background-color: var(--meta-subtle-color);
  color: var(--root-color);
  cursor: pointer;
}

.fastnav-block {
  color: var(--root-color);
}
```

```space-lua
fastnav = fastnav or {}

-- Default configuration
local DEFAULT_CONFIG = {
  tags = {},
  filterMode = "exclude",
  matchMode = "exact",
  pageSize = 25
}

-- Fetch all relevant page and tag data
local function fetchTagAndPageData(dir)
  return query[[
  from p = index.tag "page"
  where p.name.startsWith(dir)
  order by p.name 
  select {
      name = p.name,
      tags = p.tags
    }
  ]]
end

-- Merge user config with defaults
local function mergeConfig(userConfig)
  local config = {}
  for k, v in pairs(DEFAULT_CONFIG) do
    config[k] = v
  end
  if userConfig then
    for k, v in pairs(userConfig) do
      config[k] = v
    end
  end
  return config
end

-- Check if a tag matches the filter
local function tagMatchesFilter(tag, filterTags, matchMode)
  if #filterTags == 0 then
    return false
  end
  
  for _, filterTag in ipairs(filterTags) do
    if matchMode == "prefix" then
      if string.startsWith(tag, filterTag) then
        return true
      end
    else -- exact match
      if tag == filterTag then
        return true
      end
    end
  end
  return false
end

-- Check if a page should be filtered out
local function shouldFilterPage(pageTags, config)
  if #config.tags == 0 then
    return false -- No filtering
  end
  
  for _, tag in ipairs(pageTags or {}) do
    local matches = tagMatchesFilter(tag, config.tags, config.matchMode)
    if config.filterMode == "exclude" and matches then
      return true -- Exclude this page
    elseif config.filterMode == "include" and matches then
      return false -- Keep this page
    end
  end
  
  -- If include mode and no matches, filter out
  if config.filterMode == "include" then
    return true
  end
  
  return false
end

-- Analyse all pages: count tags, check for untagged pages
local function analyseTags(data, config)
  local tagCounts = {}
  local hasUntagged = false
  
  for _, page in ipairs(data) do
    local tags = page.tags or {}
    
    -- Skip pages that should be filtered
    if not shouldFilterPage(tags, config) then
      -- Check for untagged pages
      if #tags == 0 then
        hasUntagged = true
      else
        -- Count tags for this page
        for _, tag in ipairs(tags) do
          -- In exclude mode: don't count tags that match the filter (we're excluding them)
          -- In include mode: only count tags that match the filter (we're including only those)
          local matches = tagMatchesFilter(tag, config.tags, config.matchMode)
          
          if config.filterMode == "exclude" then
            if not matches then
              tagCounts[tag] = (tagCounts[tag] or 0) + 1
            end
          elseif config.filterMode == "include" then
            if matches then
              tagCounts[tag] = (tagCounts[tag] or 0) + 1
            end
          else
            -- No filtering, count all tags
            tagCounts[tag] = (tagCounts[tag] or 0) + 1
          end
        end
      end
    end
  end
  
  return tagCounts, hasUntagged
end

-- Convert tag count map to sorted array
local function sortedTagList(counts)
  local tags = {}
  for tag, count in pairs(counts) do
    table.insert(tags, {name = tag, count = count})
  end
  table.sort(tags, function(a, b) return a.name < b.name end)
  return tags
end

-- Generate HTML for all tags
function fastnav.TagsHtml(data, config)
  local tagCounts, hasUntagged = analyseTags(data, config)
  local sortedTags = sortedTagList(tagCounts)
  
  local html = {}
  table.insert(html, fastnav.TagHtml("AllTags"))
  if hasUntagged then
    table.insert(html, fastnav.TagHtml("NoTags"))
  end
  
  for _, tag in ipairs(sortedTags) do
    table.insert(html, fastnav.TagHtml(tag.name, tag.count))
  end
  
  return html
end

-- Generate HTML for all pages
function fastnav.PagesHtml(data, config)
  local html = {}
  
  for _, page in ipairs(data) do
    local tags = page.tags or {}
    
    -- Skip filtered pages
    if not shouldFilterPage(tags, config) then
      -- Prepare tag list for display
      local displayTags = {}
      if #tags == 0 then
        displayTags = {"NoTags"}
      else
        for _, tag in ipairs(tags) do
          -- In exclude mode: don't show tags that match the filter
          -- In include mode: only show tags that match the filter
          local matches = tagMatchesFilter(tag, config.tags, config.matchMode)
          
          if config.filterMode == "exclude" then
            if not matches then
              table.insert(displayTags, tag)
            end
          elseif config.filterMode == "include" then
            if matches then
              table.insert(displayTags, tag)
            end
          else
            -- No filtering, show all tags
            table.insert(displayTags, tag)
          end
        end
        -- If all tags were filtered out, use NoTags
        if #displayTags == 0 then
          displayTags = {"NoTags"}
        end
      end
      
      table.insert(html, fastnav.PageHtml(page.name, displayTags))
    end
  end
  
  return html
end

-- Individual page blocks
function fastnav.PageHtml(name, tagList)
  local tagClass = table.concat(tagList, " ")
  local basename = string.match(name, "[^/]+$") or name
  local escapedName = string.gsub(name, "'", "\\'")
  return string.format(
    '<span onclick="window.location=\'%s\';" class="%s">%s</span>',
    escapedName,
    tagClass,
    basename
  )
end

-- Generate the initialization code that sets up all pagination functions
local function generateInitCode(pageSize)
  return string.format([[
if (!window.fastnavInit) {
  window.fastnavInit = true;
  window.fastnavCurrentPage = 1;
  window.fastnavPageSize = %d;
  
  window.fastnavUpdatePagination = function() {
    const pages = document.querySelectorAll('.fastnav-pages span');
    const visiblePages = [];
    
    // First, hide all pages
    for (let i = 0; i < pages.length; i++) {
      pages[i].style.display = 'none';
    }
    
    // Collect pages that aren't filtered by tags
    for (let i = 0; i < pages.length; i++) {
      if (pages[i].getAttribute('data-hidden') !== 'true') {
        visiblePages.push(pages[i]);
      }
    }
    
    const totalPages = Math.ceil(visiblePages.length / window.fastnavPageSize);
    if (totalPages === 0) {
      window.fastnavCurrentPage = 1;
    } else {
      window.fastnavCurrentPage = Math.min(window.fastnavCurrentPage, totalPages);
    }
    const startIdx = (window.fastnavCurrentPage - 1) * window.fastnavPageSize;
    const endIdx = startIdx + window.fastnavPageSize;
    
    // Show only the pages in the current page range
    for (let i = 0; i < visiblePages.length; i++) {
      if (i >= startIdx && i < endIdx) {
        visiblePages[i].style.display = 'inline';
      }
    }
    
    const pageInfo = document.querySelector('.fn-page-info');
    const prevBtn = document.querySelector('.fn-prev');
    const nextBtn = document.querySelector('.fn-next');
    if (pageInfo) {
      pageInfo.textContent = visiblePages.length === 0 ? 'No pages' : 'Page ' + window.fastnavCurrentPage + ' of ' + totalPages + ' (' + visiblePages.length + ' pages)';
    }
    if (prevBtn) prevBtn.disabled = window.fastnavCurrentPage <= 1;
    if (nextBtn) nextBtn.disabled = window.fastnavCurrentPage >= totalPages || totalPages === 0;
  };
  
  window.fastnavPrevPage = function() {
    if (window.fastnavCurrentPage > 1) {
      window.fastnavCurrentPage--;
      window.fastnavUpdatePagination();
    }
  };
  
  window.fastnavNextPage = function() {
    const pages = document.querySelectorAll('.fastnav-pages span');
    const visiblePages = [];
    for (let i = 0; i < pages.length; i++) {
      if (pages[i].getAttribute('data-hidden') !== 'true') {
        visiblePages.push(pages[i]);
      }
    }
    const totalPages = Math.ceil(visiblePages.length / window.fastnavPageSize);
    if (window.fastnavCurrentPage < totalPages) {
      window.fastnavCurrentPage++;
      window.fastnavUpdatePagination();
    }
  };
}
]], pageSize)
end

-- Generate JavaScript for tag filtering
local function generateTagScript(tagName, pageSize)
  local initCode = generateInitCode(pageSize)
  
  if tagName == "AllTags" then
    return initCode .. [[
window.activeTags = [];
const tags = document.getElementsByClassName('fn-tag');
for (let i = 0; i < tags.length; i++) {
  tags[i].classList.remove('active-tag');
}
event.currentTarget.classList.add('active-tag');
const pages = document.querySelectorAll('.fastnav-pages span');
for (let i = 0; i < pages.length; i++) {
  pages[i].removeAttribute('data-hidden');
}
window.fastnavCurrentPage = 1;
window.fastnavUpdatePagination();
]]
  else
    local escapedTag = string.gsub(tagName, "'", "\\'")
    return initCode .. string.format([[
window.activeTags = window.activeTags || [];
const tagName = '%s';
const index = window.activeTags.indexOf(tagName);
if (index === -1) {
  window.activeTags.push(tagName);
  event.currentTarget.classList.add('active-tag');
  const allBtn = document.querySelector('.fn-tag.AllTags');
  if (allBtn) allBtn.classList.remove('active-tag');
} else {
  window.activeTags.splice(index, 1);
  event.currentTarget.classList.remove('active-tag');
  if (window.activeTags.length === 0) {
    const allBtn = document.querySelector('.fn-tag.AllTags');
    if (allBtn) allBtn.classList.add('active-tag');
  }
}
const pages = document.querySelectorAll('.fastnav-pages span');
for (let i = 0; i < pages.length; i++) {
  const pageClasses = pages[i].className.split(' ');
  let shouldShow = false;
  for (let j = 0; j < window.activeTags.length; j++) {
    if (pageClasses.indexOf(window.activeTags[j]) !== -1) {
      shouldShow = true;
      break;
    }
  }
  if (window.activeTags.length === 0 || shouldShow) {
    pages[i].removeAttribute('data-hidden');
  } else {
    pages[i].setAttribute('data-hidden', 'true');
  }
}
window.fastnavCurrentPage = 1;
window.fastnavUpdatePagination();
]], escapedTag)
  end
end

-- Individual tag buttons
function fastnav.TagHtml(name, count, pageSize)
  local script = generateTagScript(name, pageSize)
  local countHtml = ""
  if count and count ~= "" then
    countHtml = string.format('<span class="fn-c">(%s)</span>', count)
  end
  local activeClass = (name == "AllTags") and " active-tag" or ""
  
  return string.format(
    '<button class="sb-command-button fn-tag %s%s" onclick="%s">%s%s</button>',
    name,
    activeClass,
    script,
    name,
    countHtml
  )
end

-- Generate pagination controls HTML with inline handlers
local function generatePaginationControls(pageSize)
  local initCode = generateInitCode(pageSize)
  return string.format([[
<div class="fn-pagination">
  <button class="sb-command-button fn-prev" onclick="%swindow.fastnavPrevPage();">← Prev</button>
  <span class="fn-page-info">Page 1 of 1</span>
  <button class="sb-command-button fn-next" onclick="%swindow.fastnavNextPage();">Next →</button>
</div>
]], initCode, initCode)
end

-- Generate trigger to initialize pagination after DOM loads
local function generateInitTrigger(pageSize)
  local initCode = generateInitCode(pageSize)
  return string.format([[
<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" onload="%ssetTimeout(function(){if(window.fastnavUpdatePagination)window.fastnavUpdatePagination();},10);this.onload=null;" style="display:none" />
]], initCode)
end

-- Main widget function
function fastnav.Widget(dir, options)
  local config = mergeConfig(options)
  local data = fetchTagAndPageData(dir)
  
  -- Pass pageSize to TagsHtml
  local tagHtmls = {}
  local tagCounts, hasUntagged = analyseTags(data, config)
  local sortedTags = sortedTagList(tagCounts)
  
  table.insert(tagHtmls, fastnav.TagHtml("AllTags", nil, config.pageSize))
  if hasUntagged then
    table.insert(tagHtmls, fastnav.TagHtml("NoTags", nil, config.pageSize))
  end
  
  for _, tag in ipairs(sortedTags) do
    table.insert(tagHtmls, fastnav.TagHtml(tag.name, tag.count, config.pageSize))
  end
  
  local pages = fastnav.PagesHtml(data, config)
  
  local tagsHtml = '<div class="fastnav-tags">' .. table.concat(tagHtmls, " ") .. '</div>'
  local pagesHtml = '<div class="fastnav-pages">' .. table.concat(pages, " ") .. '</div>'
  local headerHtml = string.format(
    "<b>Pages:</b> %d <b>Tags:</b> %d",
    #pages,
    #tagHtmls
  )
  
  local paginationControls = generatePaginationControls(config.pageSize)
  local initTrigger = generateInitTrigger(config.pageSize)
  
  return widget.new {
    html = headerHtml .. tagsHtml .. pagesHtml .. paginationControls .. initTrigger,
    display = "block",
    cssClasses = {"fastnav-block"}
  }
end
```