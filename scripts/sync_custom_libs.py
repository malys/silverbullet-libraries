#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Helper function to run shell commands"""
    import subprocess
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        return (True, result.stdout.strip())
    except subprocess.CalledProcessError as e:
        return (False, f"Error: {e.stderr.strip()}")

def has_description_frontmatter(file_path):
    """Check if a markdown file has a description in its frontmatter.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        bool: True if the file has a description in frontmatter, False otherwise
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        # Look for frontmatter between triple-dashed lines
        frontmatter_match = re.search(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            # Check for description field in frontmatter (case insensitive)
            return bool(re.search(r'^description\s*:', frontmatter, re.MULTILINE | re.IGNORECASE))
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def sync_custom_libraries():
    # Base directories
    current_dir = Path('.').resolve()
    source_dir = current_dir.parent / 'silverbullet_backup' / 'z-custom'
    src_dir = current_dir / 'src'
    
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return False
        
    # Update source repository
    print("Updating source repository...")
    success, output = run_command("git pull", cwd=source_dir)
    if not success:
        print(f"Warning: Failed to update source repository: {output}")
    else:
        print("Source repository updated successfully")
    

    # Remove src folder
    print("\nRemoving src/ folder...")
    try:
        shutil.rmtree(src_dir)
        print("src/ folder removed successfully")
    except FileNotFoundError:
        print(f"src/ folder not found")
    except Exception as e:
        print(f"Error removing src/ folder: {e}")
   
    # Create src directory if it doesn't exist
    src_dir = current_dir / 'src'
    src_dir.mkdir(exist_ok=True)
    
    # First, collect all files to copy (excluding test files, Templates folder, and files without description)
    print("\nScanning for files to copy...")
    files_to_copy = []
    skipped_files = 0
    
    for src_file in source_dir.rglob('*.md'):
        # Skip test files, Templates, and import folders
        skip_patterns = ['test', 'Templates', 'import']
        if any(pattern.lower() in str(src_file).lower() for pattern in skip_patterns):
            print(f"Skipping (excluded pattern): {src_file.relative_to(source_dir)}")
            skipped_files += 1
            continue
            
        # Check for description in frontmatter
        if has_description_frontmatter(src_file):
            files_to_copy.append(src_file)
            print(f"Including (has description): {src_file.relative_to(source_dir)}")
        else:
            print(f"Skipping (no description): {src_file.relative_to(source_dir)}")
            skipped_files += 1
    
    print(f"\nFound {len(files_to_copy)} files with descriptions, skipped {skipped_files} files")
    
    if not files_to_copy:
        print("No files to copy after filtering.")
        return True
        
    # Now copy the files
    print(f"\nCopying {len(files_to_copy)} files to src/...")
    for src_file in files_to_copy:
        try:
            # Get the relative path and create destination path in src/
            rel_path = src_file.relative_to(source_dir)
            dest_file = src_dir / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(src_file, dest_file)
            print(f"Copied to src/: {rel_path}")
        except Exception as e:
            print(f"Error copying {src_file}: {e}")
    
    print("\nSync completed!")
    return True

if __name__ == "__main__":
    sync_custom_libraries()
