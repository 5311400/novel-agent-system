"""
novel-agent-system data validator.

Scans data/ directory, extracts all defined IDs and cross-references,
reports broken links and consistency issues.

Usage:
    python tools/validate.py              # validate data/ directory
    python tools/validate.py --verbose    # show all refs, not just broken ones
    python tools/validate.py --silent     # exit code only (0=ok, 1=issues found)

Exit code:
    0 = all checks passed
    1 = issues found
"""

import re
import sys
import os
from pathlib import Path


# --- Configuration ---
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REQUIRED_DIRS = ["world", "characters"]
ID_PATTERN = re.compile(r"\[\[([a-z_]+):([a-z0-9_-]+)\]\]")


# --- ID Extraction ---

def extract_definitions(filepath):
    """Extract all defined IDs from a .md file.
    
    Definitions are recognized from:
    - Section headers: "## [[type:id]] Name"
    - YAML fields: "char_id: xxx" / "faction_id: xxx" / "id: xxx"
    """
    definitions = set()
    text = filepath.read_text("utf-8", errors="replace")
    
    for line in text.split("\n"):
        # Pattern 1: Section headers only (lines starting with #)
        stripped = line.strip()
        if stripped.startswith("#"):
            for m in ID_PATTERN.finditer(line):
                definitions.add((m.group(1), m.group(2)))
        
        # Pattern 2: "char_id: xxx" / "faction_id: xxx" / "geography_id: xxx"
        id_match = re.match(r"^\s*(?:char_id|faction_id|geo_id|power_id|id)\s*:\s*['\"]?([a-z0-9_-]+)", line, re.IGNORECASE)
        if id_match:
            obj_id = id_match.group(1)
            # Infer type from filename or field name
            if "faction" in line.lower():
                definitions.add(("faction", obj_id))
            elif "char" in line.lower():
                definitions.add(("character", obj_id))
            elif "geo" in line.lower():
                definitions.add(("geo", obj_id))
            elif "power" in line.lower():
                definitions.add(("power", obj_id))
            else:
                definitions.add(("unknown", obj_id))
    
    return definitions


def extract_references(filepath):
    """Extract all [[type:id]] cross-references from a .md file."""
    text = filepath.read_text("utf-8", errors="replace")
    return set(ID_PATTERN.findall(text))


# --- Validators ---

def validate_cross_references(project_dir, verbose=False):
    """Main validation: check all [[type:id]] references resolve."""
    data_dir = Path(project_dir) / "data"
    if not data_dir.exists():
        return [f"ERROR: data/ directory not found at {data_dir}"]

    # Collect all .md files
    md_files = list(data_dir.rglob("*.md"))
    md_files = [f for f in md_files if ".example" not in f.suffixes]
    
    if not md_files:
        return ["WARNING: no .md files found in data/ (everything looks clean)"]
    
    # Build definition set and reference set
    all_defs = set()
    all_refs = set()
    file_defs = {}
    file_refs = {}
    
    for f in md_files:
        defs = extract_definitions(f)
        refs = extract_references(f)
        file_defs[f.relative_to(data_dir.parent)] = defs
        file_refs[f.relative_to(data_dir.parent)] = refs
        all_defs.update(defs)
        all_refs.update(refs)
    
    # Self-references don't count (a file can define [[geo:valley]] and also use it)
    # But we need to handle the fact that a ref in file X might be defined in file X itself
    
    # Find broken references
    broken = []
    for f, refs in file_refs.items():
        for type_, id_ in refs:
            # Check if this ref is defined ANYWHERE (including the same file)
            if (type_, id_) not in all_defs:
                # Special case: some refs might use "self" definitions in the same file
                # If the file defines it, it's fine
                if (type_, id_) not in file_defs.get(f, set()):
                    broken.append((f, type_, id_))
    
    issues = []
    if broken:
        issues.append(f"FOUND {len(broken)} BROKEN REFERENCES:")
        for f, type_, id_ in sorted(broken):
            issues.append(f"  {f}  -> [[{type_}:{id_}]]  NOT FOUND")
        broken_ids = {id_ for _, _, id_ in broken}
        issues.append(f"  Total unique broken IDs: {len(broken_ids)}")
    else:
        issues.append("All cross-references resolve correctly [OK]")
    
    if verbose:
        issues.append(f"\n--- Summary ---")
        issues.append(f"Files scanned:    {len(md_files)}")
        issues.append(f"Definitions:     {len(all_defs)}")
        issues.append(f"References:      {len(all_refs)}")
        issues.append(f"Broken refs:     {len(broken)}")
        
        # Show all definitions (sorted)
        issues.append("\nDefined IDs:")
        for type_, id_ in sorted(all_defs):
            issues.append(f"  [{type_}] {id_}")
        
        issues.append("\nAll References:")
        for f, refs in sorted(file_refs.items()):
            for type_, id_ in sorted(refs):
                issues.append(f"  {f} -> [{type_}] {id_}")
    
    return issues


def validate_index_md(project_dir):
    """Check INDEX.md format and version numbers."""
    index_path = Path(project_dir) / "data" / "INDEX.md"
    if not index_path.exists():
        return ["WARNING: data/INDEX.md not found"]
    
    text = index_path.read_text("utf-8")
    issues = []
    
    # Check required version fields
    versions = re.findall(r"-\s*([\w-]+):\s*(\d+)", text)
    found_keys = {k: int(v) for k, v in versions}
    
    required = ["GV", "WV", "CV", "CH-V"]
    for key in required:
        if key not in found_keys:
            issues.append(f"WARNING: INDEX.md missing version field '{key}'")
        else:
            val = found_keys[key]
            if not isinstance(val, int) or val < 0:
                issues.append(f"WARNING: INDEX.md '{key}' has invalid value: {val}")
    
    if not issues:
        issues.append("INDEX.md format valid [OK]")
    
    return issues


def run_all(project_dir=".", verbose=False):
    """Run all validators and return issues list."""
    data_dir = Path(project_dir) / "data"
    issues = []
    
    issues.append(f"=== novel-agent-system data validation ===")
    issues.append(f"Data directory: {data_dir.resolve()}")
    issues.append("")
    
    # 1. Cross-reference validation
    issues.append("--- Cross-Reference Check ---")
    issues.extend(validate_cross_references(project_dir, verbose))
    issues.append("")
    
    # 2. INDEX.md check
    issues.append("--- INDEX.md Check ---")
    issues.extend(validate_index_md(project_dir))
    issues.append("")
    
    return issues


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="novel-agent-system data validator")
    parser.add_argument("--path", default=".", help="Project root path (default: current dir)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all references")
    parser.add_argument("--silent", "-s", action="store_true", help="Exit code only, no output")
    
    args = parser.parse_args()
    
    issues = run_all(args.path, verbose=args.verbose)
    
    if not args.silent:
        for line in issues:
            print(line)
    
    has_errors = any(line.startswith("FOUND") or line.startswith("ERROR") for line in issues)
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()


