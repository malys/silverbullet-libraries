#!/usr/bin/env python3
import os
import re
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Configuration constants
NAME = "malys"
REPOSITORY = f"{NAME}/silverbullet-libraries"
SOURCE_PATH = "src/"

def get_markdown_files(directory, exclude=None):
    if exclude is None:
        exclude = []
    markdown_files = []
    for file_path in Path(directory).glob('**/*.md'):
        if file_path.name not in exclude and not any(part.startswith('.') for part in file_path.parts):
            markdown_files.append(file_path)
    return sorted(markdown_files)

def fix_markdown_links(text):
    """Fix malformed Markdown links in the text."""
    if not text:
        return text
    # Fix patterns like 'text](url)' to '[text](url)'
    return re.sub(r'(?<![\[\]\w])([\w\s-]+)(]\()', r'[\1\2', text, flags=re.UNICODE)

def get_description(file_path):
    """Extract the description from a markdown file's frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                # Look for both quoted and unquoted descriptions
                desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
                if desc_match:
                    description = desc_match.group(1).strip()
                    if not description:
                        # If empty quoted string, try to get the first line after the header
                        content_after_frontmatter = content[frontmatter_match.end():].strip()
                        first_line = content_after_frontmatter.split('\n', 1)[0].strip()
                        if first_line and not first_line.startswith('#'):
                            return first_line
                    return fix_markdown_links(description)
                # If no description in frontmatter, try to get first line after frontmatter
                content_after_frontmatter = content[frontmatter_match.end():].strip()
                first_line = content_after_frontmatter.split('\n', 1)[0].strip()
                if first_line and not first_line.startswith('#'):
                    return first_line
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
    return None

def get_last_commit_date(file_path):
    """Get the last commit date of a file in a human-readable format."""
    try:
        cmd = ['git', 'log', '-1', '--format=%cI', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            date_str = result.stdout.strip()
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%Y-%m-%d')
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Warning: Could not get commit date for {file_path}: {e}")
    return None

def generate_readme():
    """Generate README.md file with library information."""
    lib_files = get_markdown_files(SOURCE_PATH, ['README.md'])
    lib_files.sort(key=lambda x: str(x).lower())
    
    content = [
        "# 🚀 SilverBullet Libraries",
        f"\nA curated collection of plugins, templates, and utilities for [SilverBullet](https://silverbullet.md/).\n",
        "## 📦 Available Libraries",
        ""
    ]
    
    for file in lib_files:
        rel_path = file.relative_to(f'./{SOURCE_PATH}')
        if 'template' in str(rel_path).lower():
            continue
            
        display_name = ' '.join(word.capitalize() for word in rel_path.stem.split('-'))
        url = f"https://github.com/{REPOSITORY}/blob/main/{SOURCE_PATH}{rel_path.as_posix().replace('\\', '/')}"
        description = get_description(file)
        last_commit = get_last_commit_date(file)
        date_suffix = f" - ({last_commit})" if last_commit else ""
        
        if description:
            content.append(f"- [{display_name}]({url}) - {description}{date_suffix}")
        else:
            content.append(f"- [{display_name}]({url}){date_suffix}")

    content.extend([
        "\n## 🛠️ Installation",
        f"1. Navigate to your `Library Manager` inside Silverbullet\n"
        f"2. Add my repository: `https://github.com/{REPOSITORY}/blob/main/Repository/{NAME}.md`\n"
        "3. Add any script my repository\n",
        "## 🤝 Contributing",
        "We welcome contributions! Here's how you can help:",
        "- Add new libraries or improve existing ones",
        "- Fix bugs or improve documentation",
        "- Suggest new features or report issues\n",
        "To contribute:",
        "1. Fork this repository",
        "2. Create a new branch for your changes",
        "3. Submit a pull request\n",
        "## 📜 License",
        "This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details."
    ])
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    print("Successfully generated README.md")

def generate_repository_file():
    """Generate Repository/NAME.md file with library information."""
    lib_files = get_markdown_files(SOURCE_PATH, ['README.md'])
    lib_files.sort(key=lambda x: str(x).lower())
    
    content = ['---',
        f'name: "Repository/{NAME} Repo"',
        'tags: meta/repository',
        'pageDecoration.prefix: "🦩"',
        '---',
        '```#meta/library/remote'
    ]

    for file in lib_files:
        rel_path = file.relative_to(f'./{SOURCE_PATH}')
        file_name = rel_path.stem
        
        if 'template' in str(rel_path).lower():
            continue
            
        display_name = ' '.join(word.capitalize() for word in file_name.split('-'))
        description = get_description(file) or f"{display_name} library"
        file_url = f'https://github.com/{REPOSITORY}/blob/main/{SOURCE_PATH}{rel_path.as_posix().replace("\\", "/")}'
        
        library_entry = [
            f'name: "{display_name}"',
            f'uri: {file_url}',
            f'website: {file_url}',
            f'description: "{description}"',
            '---'
        ]
        
        content.extend(library_entry)
    
    content.append('```')
    
    os.makedirs('Repository', exist_ok=True)
    
    with open(f'Repository/{NAME}.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print(f"Successfully generated Repository/{NAME}.md")

def main():
    parser = argparse.ArgumentParser(description='Generate repository files.')
    parser.add_argument('--readme', action='store_true', help='Generate README.md')
    parser.add_argument('--index', action='store_true', help=f'Generate Repository/{NAME}.md')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    if args.readme:
        generate_readme()
    if args.index:
        generate_repository_file()

if __name__ == "__main__":
    main()
