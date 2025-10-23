"""
SilverBullet Community Library Introspector
-------------------------------------------
Fetches the list of external SilverBullet libraries from the community page,
extracts metadata from linked GitHub repositories, saves structured data to JSON,
and prints a formatted summary message.

Requirements:
    pip install requests beautifulsoup4
"""

import requests
import json
from bs4 import BeautifulSoup

COMMUNITY_URL = "https://community.silverbullet.md/t/external-libraries-from-sb-community/3414"
OUTPUT_FILE = "silverbullet_libraries.json"


def fetch_page(url):
    print(f"🔹 Fetching {url} ...")
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.text


def parse_library_list(html):
    """Extract GitHub repository links from HTML anchor tags in the forum post."""
    soup = BeautifulSoup(html, 'html.parser')

    # Find all anchor tags with href attributes
    links = soup.find_all('a', href=True)

    libs = []
    processed_urls = set()  # Track processed repository URLs to avoid duplicates
    
    for link in links:
        url = link['href'].strip()
        # Only include GitHub URLs
        # Exclude the summary file from the community page
        if url != 'https://github.com/malys/silverbullet-libraries/blob/main/space_scripts_summary.md' and 'github.com' in url:
            # Normalize URL to handle different formats (with/without .git, http/https, etc.)
            normalized_url = url.lower().replace('.git', '').rstrip('/')
            if 'http://' in normalized_url:
                normalized_url = normalized_url.replace('http://', 'https://')
            
            # Skip if we've already processed this repository
            if normalized_url in processed_urls:
                continue
                
            name = link.get_text().strip()
            # Skip empty names or navigation links
            if name and not any(skip in name.lower() for skip in ['home', 'categories', 'guidelines', 'terms', 'privacy']):
                libs.append({"name": name, "url": url})
                processed_urls.add(normalized_url)

    return libs


def fetch_github_metadata(lib):
    """Fetch metadata (author, description, stars, etc.) from GitHub API."""
    if "github.com" not in lib["url"]:
        return lib

    parts = lib["url"].split("/")
    if len(parts) < 5:
        return lib

    owner, repo = parts[3], parts[4]
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        r = requests.get(api_url, headers={"User-Agent": "SilverBullet-Introspector"})
        if r.status_code == 200:
            data = r.json()
            lib.update({
                "author": data.get("owner", {}).get("login"),
                "description": data.get("description"),
                "stars": data.get("stargazers_count"),
                "last_updated": data.get("updated_at"),
                "category": infer_category(data.get("description") or "")
            })
        else:
            print(f"⚠️  GitHub API error for {repo}: {r.status_code}")
    except Exception as e:
        print(f"⚠️  Error fetching metadata for {repo}: {e}")
    return lib


def infer_category(description):
    """Infer a simple category based on description text."""
    if not description:
        return "unknown"
    desc = description.lower()
    if "theme" in desc:
        return "theme"
    if "plugin" in desc or "plug" in desc:
        return "plugin"
    if "template" in desc:
        return "template"
    if "library" in desc:
        return "library"
    return "misc"


def generate_markdown_summary(libraries):
    """Generate a Markdown-style summary message."""
    lines = ["List of current scripts:"]
    for lib in libraries:
        name = lib.get("name", "Unnamed")
        url = lib.get("url", "#")
        author = lib.get("author", "unknown author")
        lines.append(f"- [{name}]({url}) from {author}")
    return "\n".join(lines)


def find_space_scripts_in_repo(owner, repo):
    """Find markdown files containing 'space-lua' or 'space-style' in a GitHub repository."""
    scripts = []

    def scan_contents(contents_url, path=""):
        """Recursively scan repository contents."""
        try:
            r = requests.get(contents_url, headers={"User-Agent": "SilverBullet-Introspector"})
            if r.status_code != 200:
                return

            contents = r.json()

            for item in contents:
                item_path = f"{path}/{item['name']}" if path else item['name']

                if item['type'] == 'file' and item['name'].endswith('.md'):
                    # Check if filename contains space-lua or space-style
                    if 'space-lua' in item['name'].lower() or 'space-style' in item['name'].lower():
                        scripts.append({
                            'name': item['name'],
                            'path': item_path,
                            'download_url': item['download_url'],
                            'repo': f"{owner}/{repo}"
                        })
                    else:
                        # Check file content for space-lua or space-style
                        try:
                            content_r = requests.get(item['download_url'], headers={"User-Agent": "SilverBullet-Introspector"})
                            if content_r.status_code == 200:
                                content = content_r.text.lower()
                                if 'space-lua' in content or 'space-style' in content:
                                    scripts.append({
                                        'name': item['name'],
                                        'path': item_path,
                                        'download_url': item['download_url'],
                                        'repo': f"{owner}/{repo}"
                                    })
                        except Exception as e:
                            print(f"⚠️  Error reading {item['name']}: {e}")

                elif item['type'] == 'dir':
                    # Recursively scan directories
                    scan_contents(item['url'], item_path)

        except Exception as e:
            print(f"⚠️  Error scanning {repo}/{path}: {e}")

    # Start scanning from root
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    scan_contents(api_url)


    return scripts


def generate_summary_message(libraries, file_url):
    """Generate a markdown message listing all space-lua and space-style scripts from repositories."""
    print("🔍 Scanning repositories for space-lua and space-style scripts...")

    all_scripts = []
    for lib in libraries:
        if "github.com" in lib.get("url", ""):
            parts = lib["url"].split("/")
            if len(parts) >= 5:
                owner, repo = parts[3], parts[4]
                print(f"  📂 Scanning {owner}/{repo}...")

                scripts = find_space_scripts_in_repo(owner, repo)
                all_scripts.extend(scripts)

    # Generate markdown message
    lines = ["# SilverBullet Space Scripts", ""]
    lines.append(f"Found space-lua and space-style scripts across defined repositories.")
    lines.append("")

    if all_scripts:
        lines.append("## Available Scripts")
        lines.append("")

        # Group by repository
        scripts_by_repo = {}
        for script in all_scripts:
            repo = script['repo']
            if repo not in scripts_by_repo:
                scripts_by_repo[repo] = []
            scripts_by_repo[repo].append(script)

        for repo, scripts in scripts_by_repo.items():
            lines.append(f"### {repo}")
            lines.append("")
            
            # Filter scripts to remove duplicate entries based on script['name']
            seen_names = set()
            scripts = [s for s in scripts if not (s['name'] in seen_names or seen_names.add(s['name']))]
            
            for script in scripts:
                script_url = f"https://github.com/{repo}/blob/main/{script['path']}"
                lines.append(f"- **{script['name']}**")
                lines.append(f"  - Path: `{script['path']}`")
                lines.append(f"  - [View File]({script_url})")
                lines.append("")

        lines.append("---")
        lines.append(f"📊 **Metadata**: [View full library metadata]({file_url})")
    else:
        lines.append("No space-lua or space-style scripts found in the scanned repositories.")
        lines.append("")
        lines.append("💡 *Tip*: Make sure the repositories contain markdown files with 'space-lua' or 'space-style' in the filename or content.")

    return "\n".join(lines)


def main():
    html = fetch_page(COMMUNITY_URL)
    libraries = parse_library_list(html)
    print(f"✅ Found {len(libraries)} library entries")

    enriched = []
    for lib in libraries:
        enriched.append(fetch_github_metadata(lib))

    # Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved metadata for {len(enriched)} libraries to {OUTPUT_FILE}")

    # Update the file_url to point to the correct GitHub repository
    # This will be set by the GitHub Actions workflow
    file_url = "https://github.com/silverbulletmd/silverbullet-libraries/blob/main/" + OUTPUT_FILE

    summary_message = generate_summary_message(enriched, file_url)
    print("\n" + summary_message)

    # Save the summary to a markdown file
    with open("space_scripts_summary.md", "w", encoding="utf-8") as f:
        f.write(summary_message)
    print("💾 Saved summary to space_scripts_summary.md")


if __name__ == "__main__":
    main()
