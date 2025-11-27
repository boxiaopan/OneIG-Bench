#!/usr/bin/env python3
"""
Script to reorganize images by prompt matching to benchmark.
Matches each sample's prompt.txt content against the benchmark CSV prompts.
"""

import os
import csv
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Category to subfolder mapping
CATEGORY_MAP = {
    "Anime_Stylization": "anime",
    "Portrait": "human",
    "General_Object": "object",
    "Text_Rendering": "text",
    "Knowledge_Reasoning": "reasoning",
    "Multilingualism": "multilingualism"
}

def load_benchmark_by_prompt(csv_path: str) -> Dict[str, Tuple[str, str]]:
    """
    Load benchmark CSV and return dict mapping prompt content to (id, category).
    
    Returns:
        Dict mapping prompt text -> (bench_id, category)
    """
    prompt_map = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check for prompt_en (English) or prompt_cn (Chinese) column
            prompt = row.get('prompt_en') or row.get('prompt_cn', '')
            prompt = prompt.strip()
            if prompt:
                prompt_map[prompt] = (row['id'], row['category'])
    
    return prompt_map

def determine_model_name(dir_name: str) -> str:
    """Determine model name from directory name."""
    if '_ep_' in dir_name or 'ep-cfg' in dir_name or 'bench_en_ep' in dir_name:
        return "omni-ep"
    else:
        return "omni"

def determine_checkpoint(dir_name: str) -> str:
    """Extract checkpoint number from directory name."""
    # Look for ckpt=XXXXX pattern
    match = re.search(r'ckpt=(\d+)', dir_name)
    if match:
        return match.group(1)
    return "unknown"

def determine_language(dir_name: str) -> str:
    """Determine language version from directory name."""
    if '_zh_' in dir_name or 'bench_zh' in dir_name:
        return "zh"
    else:
        return "en"

def determine_benchmark(dir_name: str) -> str:
    """Determine which benchmark CSV to use based on directory name."""
    if '_zh_' in dir_name or 'bench_zh' in dir_name:
        return "OneIG-Bench-ZH.csv"
    else:
        return "OneIG-Bench.csv"

def find_prompt_match(prompt_content: str, prompt_map: Dict[str, Tuple[str, str]], use_fuzzy: bool = False) -> Optional[Tuple[str, str]]:
    """
    Find a matching prompt in the benchmark.
    
    Args:
        prompt_content: The prompt text from the sample's prompt.txt
        prompt_map: Dict mapping benchmark prompts to (id, category)
        use_fuzzy: If True, check if benchmark prompt is a substring of sample prompt
    
    Returns:
        (bench_id, category) tuple if found, None otherwise
    """
    # First try exact match
    if prompt_content in prompt_map:
        return prompt_map[prompt_content]
    
    # If fuzzy matching enabled, check if any benchmark prompt is contained in the sample prompt
    if use_fuzzy:
        for benchmark_prompt, (bench_id, category) in prompt_map.items():
            if benchmark_prompt in prompt_content:
                return (bench_id, category)
    
    return None

def reorganize_directory(
    source_dir: str,
    output_dir: str,
    benchmark_csv: str,
    model_name: str,
    checkpoint: str,
    language: str,
    is_grid: bool = False,
    use_fuzzy_match: bool = False,
    use_symlinks: bool = True
) -> Tuple[int, int, int]:
    """
    Reorganize images from one source directory using prompt-based matching.
    
    Output structure: output_dir/model_name/grids|non-grids/checkpoint/language/category/
    
    Returns:
        (created_count, skipped_count, unmatched_count)
    """
    source_path = Path(source_dir)
    image_type = "grids" if is_grid else "non-grids"
    output_path = Path(output_dir) / model_name / image_type / checkpoint / language
    
    # Load benchmark by prompt content
    prompt_map = load_benchmark_by_prompt(benchmark_csv)
    print(f"  Loaded {len(prompt_map)} prompts from {benchmark_csv}")
    if use_fuzzy_match:
        print(f"  Using fuzzy matching (for expanded prompts)")
    
    # Find all sample directories
    sample_dirs = sorted([d for d in source_path.iterdir() if d.is_dir() and d.name.startswith('sample_')])
    print(f"  Found {len(sample_dirs)} sample directories")
    
    created_count = 0
    skipped_count = 0
    unmatched_samples = []  # Track all unmatched samples
    
    for sample_idx, sample_dir in enumerate(sample_dirs):
        image_file = sample_dir / "image.png"
        prompt_file = sample_dir / "prompt.txt"
        
        # Check if image exists
        if not image_file.exists():
            print(f"  Warning: No image.png in {sample_dir.name}")
            skipped_count += 1
            continue
        
        # Check if prompt.txt exists
        if not prompt_file.exists():
            print(f"  Warning: No prompt.txt in {sample_dir.name}")
            skipped_count += 1
            continue
        
        # Read the prompt content
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read().strip()
        
        # Look up the prompt in the benchmark
        match = find_prompt_match(prompt_content, prompt_map, use_fuzzy=use_fuzzy_match)
        if not match:
            # No match found - record and discard
            unmatched_samples.append((sample_dir.name, prompt_content[:80]))
            continue
        
        bench_id, category = match
        
        # Map category to subfolder
        subfolder = CATEGORY_MAP.get(category)
        if not subfolder:
            print(f"  Warning: Unknown category '{category}' for ID {bench_id}")
            skipped_count += 1
            continue
        
        # Create destination path: output_dir/model/grids|non-grids/checkpoint/category/
        dest_folder = output_path / subfolder
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_file = dest_folder / f"{bench_id}.webp"
        
        # Create symlink or copy
        if dest_file.exists():
            dest_file.unlink()
        
        if use_symlinks:
            # Create relative symlink
            rel_path = os.path.relpath(image_file, dest_folder)
            dest_file.symlink_to(rel_path)
        else:
            shutil.copy2(image_file, dest_file)
        
        created_count += 1
        
        if (sample_idx + 1) % 200 == 0:
            print(f"  Processed {sample_idx + 1}/{len(sample_dirs)} samples...")
    
    # Report all unmatched samples (discarded)
    if unmatched_samples:
        print(f"\n  Discarded {len(unmatched_samples)} samples with no exact prompt match:")
        for sample_name, prompt_preview in unmatched_samples:
            print(f"    - {sample_name}: {prompt_preview}...")
    
    return created_count, skipped_count, len(unmatched_samples)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Reorganize OneIG-Bench images using index-based matching"
    )
    parser.add_argument(
        "--source_dirs",
        nargs="+",
        required=True,
        help="Source directories containing sample_XXXXX folders"
    )
    parser.add_argument(
        "--output_dir",
        required=True,
        help="Output directory for reorganized images"
    )
    parser.add_argument(
        "--benchmark_dir",
        default=".",
        help="Directory containing OneIG-Bench.csv and OneIG-Bench-ZH.csv (default: current directory)"
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of creating symlinks"
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default=None,
        help="Override auto-detected model name (e.g., 'omni-v2'). If not set, auto-detects from directory name."
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help="Override auto-detected checkpoint (e.g., '15000'). If not set, auto-detects from directory name."
    )
    parser.add_argument(
        "--grid",
        action="store_true",
        help="Mark these images as 2x2 grids (output to 'grids' subfolder instead of 'non-grids')"
    )
    
    args = parser.parse_args()
    
    output_path = Path(args.output_dir)
    benchmark_dir = Path(args.benchmark_dir)
    
    print("=" * 80)
    print("OneIG-Bench Image Reorganization (Prompt-Based Matching)")
    print("=" * 80)
    print(f"\nOutput directory: {output_path}")
    print(f"Image type: {'grids' if args.grid else 'non-grids'}")
    print(f"Using {'copies' if args.copy else 'symlinks'}")
    print(f"\nProcessing {len(args.source_dirs)} source directories:\n")
    
    total_created = 0
    total_skipped = 0
    total_unmatched = 0
    
    for source_dir in args.source_dirs:
        source_path = Path(source_dir)
        dir_name = source_path.name
        
        print(f"\n{'=' * 80}")
        print(f"Processing: {dir_name}")
        print(f"{'=' * 80}")
        
        # Determine model name, checkpoint, language, and benchmark
        model_name = args.model_name if args.model_name else determine_model_name(dir_name)
        checkpoint = args.checkpoint if args.checkpoint else determine_checkpoint(dir_name)
        language = determine_language(dir_name)
        benchmark_file = determine_benchmark(dir_name)
        benchmark_path = benchmark_dir / benchmark_file
        
        # Auto-enable fuzzy matching for omni-ep (expanded prompts)
        use_fuzzy = (model_name == "omni-ep")
        
        print(f"  Model name: {model_name}")
        print(f"  Checkpoint: {checkpoint}")
        print(f"  Language: {language}")
        print(f"  Image type: {'grids' if args.grid else 'non-grids'}")
        print(f"  Fuzzy matching: {use_fuzzy}")
        print(f"  Benchmark: {benchmark_file}")
        
        if not benchmark_path.exists():
            print(f"  ERROR: Benchmark file not found: {benchmark_path}")
            continue
        
        if not source_path.exists():
            print(f"  ERROR: Source directory not found: {source_path}")
            continue
        
        # Process this directory
        created, skipped, unmatched = reorganize_directory(
            source_dir=source_dir,
            output_dir=args.output_dir,
            benchmark_csv=str(benchmark_path),
            model_name=model_name,
            checkpoint=checkpoint,
            language=language,
            is_grid=args.grid,
            use_fuzzy_match=use_fuzzy,
            use_symlinks=not args.copy
        )
        
        print(f"\n  Results for {model_name}:")
        print(f"    Created: {created}")
        print(f"    Skipped (missing files): {skipped}")
        print(f"    Unmatched prompts: {unmatched}")
        
        total_created += created
        total_skipped += skipped
        total_unmatched += unmatched
    
    # Print summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total created: {total_created}")
    print(f"Total skipped: {total_skipped}")
    print(f"Total unmatched prompts: {total_unmatched}")
    print(f"\nReorganized images in: {output_path}")
    
    # Show structure
    print(f"\nFinal structure:")
    if output_path.exists():
        for model_dir in sorted(output_path.iterdir()):
            if model_dir.is_dir():
                print(f"  {model_dir.name}/")
                for image_type_dir in sorted(model_dir.iterdir()):
                    if image_type_dir.is_dir():
                        print(f"    {image_type_dir.name}/")
                        for ckpt_dir in sorted(image_type_dir.iterdir()):
                            if ckpt_dir.is_dir():
                                print(f"      {ckpt_dir.name}/")
                                for lang_dir in sorted(ckpt_dir.iterdir()):
                                    if lang_dir.is_dir():
                                        print(f"        {lang_dir.name}/")
                                        for cat_dir in sorted(lang_dir.iterdir()):
                                            if cat_dir.is_dir():
                                                count = len(list(cat_dir.glob("*.webp")))
                                                print(f"          {cat_dir.name}: {count} images")

if __name__ == "__main__":
    main()