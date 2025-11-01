#!/usr/bin/env python3
import os
import re
import json
from datetime import datetime
from pathlib import Path

def get_markdown_files(directory, exclude=None):
    if exclude is None:
        exclude = []
    markdown_files = []
    for file_path in Path(directory).glob('**/*.md'):
        if file_path.name not in exclude and not any(part.startswith('.') for part in file_path.parts):
            markdown_files.append(file_path)
    return sorted(markdown_files)

def get_file_metadata(file_path):
    """Extract metadata from a markdown file's frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for frontmatter between ---
            frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            metadata = {
                'description': '',
                'author': '',
                'date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                # Look for description field
                desc_match = re.search(r'^description:\s*(.*?)(?:\n|$)', frontmatter, re.MULTILINE)
                if desc_match:
                    metadata['description'] = desc_match.group(1).strip()
                # Look for author field
                author_match = re.search(r'^author:\s*(.*?)(?:\n|$)', frontmatter, re.MULTILINE)
                if author_match:
                    metadata['author'] = author_match.group(1).strip()
                # Look for date field
                date_match = re.search(r'^date:\s*(.*?)(?:\n|$)', frontmatter, re.MULTILINE)
                if date_match:
                    metadata['date'] = date_match.group(1).strip()
            
            return metadata
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
    return None

def generate_index():
    # Get all markdown files from src directory (excluding README.md and hidden directories)
    lib_files = get_markdown_files('src', ['README.md'])
    
    index_entries = []
    
    for file in lib_files:
        rel_path = file.relative_to('src')
        
        # Skip template files in the listing
        if 'template' in str(rel_path).lower():
            continue
            
        # Get file metadata
        metadata = get_file_metadata(file)
        if not metadata:
            continue
            
        # Format the URLs
        github_url = f"https://github.com/malys/silverbullet-libraries/blob/main/src/{rel_path.as_posix()}"
        raw_url = f"https://raw.githubusercontent.com/malys/silverbullet-libraries/main/src/{rel_path.as_posix()}"
        
        # Create entry
        entry = {
            'githubUrl': github_url,
            'rawUrl': raw_url,
            'updateDate': metadata['date'],
            'lastCommitDate': metadata['date'],  # Using the same date as we don't have git history in this script
            'author': metadata['author'],
            'description': metadata['description']
        }
        index_entries.append(entry)
    
    # Write to index.json
    with open('index.json', 'w', encoding='utf-8') as f:
        json.dump(index_entries, f, indent=2, ensure_ascii=False)
    
    print(f"Generated index.json with {len(index_entries)} entries")

if __name__ == "__main__":
    generate_index()
