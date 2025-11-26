#!/usr/bin/env python3
"""
Script to reorganize images by sequential index matching to benchmark.
Assumes samples are in the same order as the benchmark CSV.
"""

import os
import csv
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Category to subfolder mapping
CATEGORY_MAP = {
    "Anime_Stylization": "anime",
    "Portrait": "human",
    "General_Object": "object",
    "Text_Rendering": "text",
    "Knowledge_Reasoning": "reasoning",
    "Multilingualism": "multilingualism"
}

def load_benchmark_by_index(csv_path: str) -> List[Tuple[str, str]]:
    """
    Load benchmark CSV and return list of (id, category) in order.
    
    Returns:
        List of (bench_id, category) tuples in order
    """
    prompts = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompts.append((row['id'], row['category']))
    
    return prompts

def determine_model_name(dir_name: str) -> str:
    """Determine model name from directory name."""
    if '_ep_' in dir_name or 'ep_cfg' in dir_name:
        return "omni-ep"
    else:
        return "omni"

def determine_benchmark(dir_name: str) -> str:
    """Determine which benchmark CSV to use based on directory name."""
    if '_zh_' in dir_name or 'bench_zh' in dir_name:
        return "OneIG-Bench-ZH.csv"
    else:
        return "OneIG-Bench.csv"

def reorganize_directory(
    source_dir: str,
    output_dir: str,
    benchmark_csv: str,
    model_name: str,
    use_symlinks: bool = True
) -> Tuple[int, int, int]:
    """
    Reorganize images from one source directory using index-based matching.
    
    Returns:
        (created_count, skipped_count, extra_count)
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # Load benchmark by index
    benchmark_entries = load_benchmark_by_index(benchmark_csv)
    print(f"  Loaded {len(benchmark_entries)} entries from {benchmark_csv}")
    
    # Find all sample directories
    sample_dirs = sorted([d for d in source_path.iterdir() if d.is_dir() and d.name.startswith('sample_')])
    print(f"  Found {len(sample_dirs)} sample directories")
    
    if len(sample_dirs) > len(benchmark_entries):
        print(f"  WARNING: {len(sample_dirs) - len(benchmark_entries)} extra samples beyond benchmark size")
    
    created_count = 0
    skipped_count = 0
    extra_count = 0
    
    for sample_idx, sample_dir in enumerate(sample_dirs):
        image_file = sample_dir / "image.png"
        
        # Check if image exists
        if not image_file.exists():
            print(f"  Warning: No image.png in {sample_dir.name}")
            skipped_count += 1
            continue
        
        # Check if we have a corresponding benchmark entry
        if sample_idx >= len(benchmark_entries):
            extra_count += 1
            continue
        
        bench_id, category = benchmark_entries[sample_idx]
        
        # Map category to subfolder
        subfolder = CATEGORY_MAP.get(category)
        if not subfolder:
            print(f"  Warning: Unknown category '{category}' for ID {bench_id}")
            skipped_count += 1
            continue
        
        # Create destination path
        dest_folder = output_path / subfolder / model_name
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
    
    return created_count, skipped_count, extra_count

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
    
    args = parser.parse_args()
    
    output_path = Path(args.output_dir)
    benchmark_dir = Path(args.benchmark_dir)
    
    print("=" * 80)
    print("OneIG-Bench Image Reorganization (Index-Based Matching)")
    print("=" * 80)
    print(f"\nOutput directory: {output_path}")
    print(f"Using {'copies' if args.copy else 'symlinks'}")
    print(f"\nProcessing {len(args.source_dirs)} source directories:\n")
    
    total_created = 0
    total_skipped = 0
    total_extra = 0
    
    for source_dir in args.source_dirs:
        source_path = Path(source_dir)
        dir_name = source_path.name
        
        print(f"\n{'=' * 80}")
        print(f"Processing: {dir_name}")
        print(f"{'=' * 80}")
        
        # Determine model name and benchmark
        model_name = args.model_name if args.model_name else determine_model_name(dir_name)
        benchmark_file = determine_benchmark(dir_name)
        benchmark_path = benchmark_dir / benchmark_file
        
        print(f"  Model name: {model_name}")
        print(f"  Benchmark: {benchmark_file}")
        
        if not benchmark_path.exists():
            print(f"  ERROR: Benchmark file not found: {benchmark_path}")
            continue
        
        if not source_path.exists():
            print(f"  ERROR: Source directory not found: {source_path}")
            continue
        
        # Process this directory
        created, skipped, extra = reorganize_directory(
            source_dir=source_dir,
            output_dir=args.output_dir,
            benchmark_csv=str(benchmark_path),
            model_name=model_name,
            use_symlinks=not args.copy
        )
        
        print(f"\n  Results for {model_name}:")
        print(f"    Created: {created}")
        print(f"    Skipped: {skipped}")
        print(f"    Extra samples (beyond benchmark): {extra}")
        
        total_created += created
        total_skipped += skipped
        total_extra += extra
    
    # Print summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total created: {total_created}")
    print(f"Total skipped: {total_skipped}")
    print(f"Total extra (not in benchmark): {total_extra}")
    print(f"\nReorganized images in: {output_path}")
    
    # Show structure
    print(f"\nFinal structure:")
    for category, subfolder in CATEGORY_MAP.items():
        cat_path = output_path / subfolder
        if cat_path.exists():
            models = [d.name for d in cat_path.iterdir() if d.is_dir()]
            if models:
                print(f"  {subfolder}/")
                for model in sorted(models):
                    count = len(list((cat_path / model).glob("*.webp")))
                    print(f"    {model}: {count} images")

if __name__ == "__main__":
    main()




