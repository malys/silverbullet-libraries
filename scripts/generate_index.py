#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

def get_markdown_files(directory, exclude=None):
    if exclude is None:
        exclude = []
    markdown_files = []
    for file_path in Path(directory).glob('**/*.md'):
        if file_path.name not in exclude and not any(part.startswith('.') for part in file_path.parts):
            markdown_files.append(file_path)
    return sorted(markdown_files)

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
                    return desc_match.group(1).strip()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
    return None

def generate_repository_file():
    # Get all markdown files from src directory (excluding README.md and hidden directories)
    lib_files = get_markdown_files('src', ['README.md'])
    
    # Sort files alphabetically
    lib_files.sort(key=lambda x: str(x).lower())
    
    # Start with the meta/library/remote block
    content = ['---',
        'name: "Repository/Malys Repo"',
        'tags: meta/repository',
        'pageDecoration.prefix: "🦩"',
        '---',
        '```#meta/library/remote'
    ]

    # Add all library entries
    for file in lib_files:
        rel_path = file.relative_to('./src')
        file_name = rel_path.stem
        
        # Skip template files in the listing
        if 'template' in str(rel_path).lower():
            continue
            
        # Format the display name (convert kebab-case to Title Case)
        display_name = ' '.join(word.capitalize() for word in file_name.split('-'))
        
        # Get description from frontmatter or use default
        description = get_description(file) or f"{display_name} library"
        
        # Format the library entry
        library_entry = [
            f'name: "{display_name}"',
            f'uri: https://github.com/malys/silverbullet-libraries/blob/main/src/{rel_path.as_posix().replace("\\", "/")}',
            f'website: https://github.com/malys/silverbullet-libraries/blob/main/src/{rel_path.as_posix().replace("\\", "/")}',
            f'description: "{description}"',
            '---'
        ]
        
        content.extend(library_entry)
    
    # Close the meta/library/remote block
    content.append('```')
    
    # Create Repository directory if it doesn't exist
    os.makedirs('Repository', exist_ok=True)
    
    # Write to Repository/Malys.md
    with open('Repository/Malys.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print("Successfully generated Repository/Malys.md")

if __name__ == "__main__":
    generate_repository_file()
