#!/usr/bin/env python3
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

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
    # Fix patterns like 'text](url)' to '[text](url)'
    return re.sub(r'(?<![\[\]\w])(\w+\s*)(]\()', r'[\1\2', text)

def get_description(file_path):
    """Extract the description from a markdown file's frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for frontmatter between ---
            frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                # Look for description field
                desc_match = re.search(r'^description:\s*(.*?)(?:\n|$)', frontmatter, re.MULTILINE)
                if desc_match:
                    description = desc_match.group(1).strip()
                    # Fix any malformed Markdown links
                    return fix_markdown_links(description)
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
    return None

def get_last_commit_date(file_path):
    """Get the last commit date of a file in a human-readable format."""
    try:
        # Get the last commit date in ISO format
        cmd = ['git', 'log', '-1', '--format=%cI', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            # Parse the ISO date and format it as YYYY-MM-DD
            date_str = result.stdout.strip()
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%Y-%m-%d')
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Warning: Could not get commit date for {file_path}: {e}")
    return None

def generate_readme():
    # Get all markdown files from src directory (excluding README.md and hidden directories)
    lib_files = get_markdown_files('src', ['README.md'])
    
    # Sort files alphabetically
    lib_files.sort(key=lambda x: str(x).lower())
    
    # Generate README content
    content = [
        "# 🚀 SilverBullet Libraries",
        "\nA curated collection of plugins, templates, and utilities for [SilverBullet](https://silverbullet.md/).\n",
        "## 📦 Available Libraries",
        ""
    ]
    
    # Add all library files in a single list
    for file in lib_files:
        rel_path = file.relative_to('./src')
        
        # Skip template files in the listing
        if 'template' in str(rel_path).lower():
            continue
            
        # Format the display name (convert kebab-case to Title Case)
        display_name = ' '.join(word.capitalize() for word in rel_path.stem.split('-'))
        url = f"https://github.com/malys/silverbullet-libraries/blob/main/src/{rel_path.as_posix().replace('\\', '/')}"
        
        # Get description from frontmatter
        description = get_description(file)
        
        # Get last commit date
        last_commit = get_last_commit_date(file)
        date_suffix = f" - ({last_commit})" if last_commit else ""
        
        # Add to content with description and date if available
        if description:
            content.append(f"- [{display_name}]({url}) - {description}{date_suffix}")
        else:
            content.append(f"- [{display_name}]({url}){date_suffix}")
    

    # Add usage instructions
    content.extend([
        "\n## 🛠️ Installation",
        "1. Navigate to your `Library Manager` inside Silverbullet\n"
        "2. Add my repository: `https://github.com/malys/silverbullet-libraries/blob/main/Repository/Malys.md`\n"
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
    
    # Write to README.md
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

if __name__ == "__main__":
    generate_readme()
