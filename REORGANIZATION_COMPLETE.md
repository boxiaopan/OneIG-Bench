# OneIG-Bench Image Reorganization - Complete

## Quick Start Workflow

### Step 1: Reorganize Images (ONE TIME ONLY)
If you have new images in the flat `sample_XXXXX` structure, run:
```bash
python3 reorganize_by_index.py \
  --source_dirs "/path/to/exp_folder_1" "/path/to/exp_folder_2" \
  --output_dir "/home/bpan/OneIG-Benchmark/images_all_models" \
  --benchmark_dir "/home/bpan/OneIG-Benchmark"
```

### Step 2: Run Evaluations
After images are reorganized, run the evaluation:
```bash
# Run both EN and ZH evaluations
./run_all_tests.sh

# OR run individually:
./run_overall.sh      # English only
./run_overall_zh.sh   # Chinese only
./run_style.sh        # Style score only (for testing)
```

**Note:** Images are already reorganized in `/home/bpan/OneIG-Benchmark/images_all_models/`. 
You only need to re-run `reorganize_by_index.py` if you generate new images.

---

## Adding New Model Variants

When you have new images from a new model variant:

### 1. Reorganize the new images
```bash
cd /home/bpan/OneIG-Benchmark

python3 reorganize_by_index.py \
  --source_dirs "/weka/cedric/YOUR_NEW_EXPERIMENT_FOLDER" \
  --output_dir "./images_all_models" \
  --benchmark_dir "."
```

The script automatically detects:
- **Model name**: Based on directory name (`_ep_` → `omni-ep`, otherwise → `omni`)
- **Benchmark**: Based on directory name (`_zh_` → ZH, otherwise → EN)

### 2. For custom model names
Use the `--model_name` flag to override auto-detection:
```bash
python3 reorganize_by_index.py \
  --source_dirs "/weka/cedric/YOUR_NEW_EXPERIMENT_FOLDER" \
  --output_dir "./images_all_models" \
  --benchmark_dir "." \
  --model_name "omni-v2"
```

### 3. Update evaluation scripts
Add your new model to the evaluation scripts:
```bash
# In run_overall.sh and run_overall_zh.sh, update:
MODEL_NAMES=("omni" "omni-ep" "omni-v2")  # Add new model
IMAGE_GRID=(1 1 1)                         # Add corresponding grid size
```

### 4. Run evaluation
```bash
./run_all_tests.sh
```

### Example: Adding a new checkpoint
```bash
# New experiment folder appears at:
# /weka/cedric/exp_32b_stage_2_0_qwen_vl_ckpt=20000_oneig_bench_en_cfg=3.5_omni_exp_32b_stage_2_0

# Step 1: Reorganize
python3 reorganize_by_index.py \
  --source_dirs "/weka/cedric/exp_32b_stage_2_0_qwen_vl_ckpt=20000_oneig_bench_en_cfg=3.5_omni_exp_32b_stage_2_0" \
  --output_dir "./images_all_models" \
  --benchmark_dir "."

# Step 2: Run eval (will evaluate all models in images_all_models/)
./run_overall.sh
```

**Note:** Symlinks are additive - running reorganize for new variants won't affect existing ones.

---

## Summary

Successfully reorganized **4,880 images** from 4 model directories into the expected OneIG-Bench evaluation structure.

## Source Directories

| Directory | Language | Model | Samples |
|-----------|----------|-------|---------|
| `exp_32b_stage_2_0_qwen_vl_ckpt=15000_oneig_bench_en_cfg=3.5_omni_exp_32b_stage_2_0` | EN | omni | 1,120 |
| `exp_32b_stage_2_0_qwen_vl_ckpt=15000_oneig_bench_en_ep_cfg=3.5_omni_exp_32b_stage_2_0` | EN | omni-ep | 1,120 |
| `exp_32b_stage_2_0_qwen_vl_ckpt=15000_oneig_bench_zh_cfg=3.5_omni_exp_32b_stage_2_0` | ZH | omni | 1,320 |
| `exp_32b_stage_2_0_qwen_vl_ckpt=15000_oneig_bench_zh_ep_cfg=3.5_omni_exp_32b_stage_2_0` | ZH | omni-ep | 1,320 |

## Output Structure

All images are now organized in `/home/bpan/OneIG-Benchmark/images_all_models/`:

```
images_all_models/
├── anime/
│   ├── omni/         (245 images: 000.webp - 244.webp)
│   └── omni-ep/      (245 images: 000.webp - 244.webp)
├── human/
│   ├── omni/         (244 images: 000.webp - 243.webp)
│   └── omni-ep/      (244 images: 000.webp - 243.webp)
├── object/
│   ├── omni/         (206 images: 000.webp - 205.webp)
│   └── omni-ep/      (206 images: 000.webp - 205.webp)
├── text/
│   ├── omni/         (200 images: 000.webp - 199.webp)
│   └── omni-ep/      (200 images: 000.webp - 199.webp)
├── reasoning/
│   ├── omni/         (225 images: 000.webp - 224.webp)
│   └── omni-ep/      (225 images: 000.webp - 224.webp)
└── multilingualism/  (ZH only)
    ├── omni/         (200 images: 000.webp - 199.webp)
    └── omni-ep/      (200 images: 000.webp - 199.webp)
```

## Mapping Method

**Index-based sequential matching**: 
- Sample directories (`sample_00000`, `sample_00001`, ...) are matched to benchmark entries by index order
- `sample_00000` → first entry in benchmark (ID 000)
- `sample_00001` → second entry in benchmark (ID 001)
- And so on...

This works because:
1. Both EN directories have exactly 1,120 samples matching OneIG-Bench.csv (1,120 entries)
2. Both ZH directories have exactly 1,320 samples matching OneIG-Bench-ZH.csv (1,320 entries)
3. Images are symlinked (not copied) for efficiency

## Scripts Created

### Reorganization Scripts

1. **`reorganize_by_index.py`** - Main reorganization script using index-based matching
   - Handles multiple source directories
   - Automatically detects model names (omni vs omni-ep)
   - Automatically detects benchmark (EN vs ZH)
   - Creates symlinks by default (use `--copy` to copy files instead)

### Evaluation Scripts

2. **`run_overall.sh`** - EN evaluation (updated)
   - Evaluates both `omni` and `omni-ep` models
   - Uses `/home/bpan/OneIG-Benchmark/images_all_models/`
   - IMAGE_GRID set to (1 1) - single images, not grids

3. **`run_overall_zh.sh`** - ZH evaluation (new)
   - Evaluates both `omni` and `omni-ep` models on Chinese benchmark
   - Includes "multilingualism" category
   - Same structure as EN version
   - IMAGE_GRID set to (1 1) - single images, not grids

## Running Evaluations

### For English (EN) Benchmark:
```bash
./run_overall.sh
```

This will evaluate:
- Alignment Score (anime, human, object)
- Text Score
- Diversity Score (anime, human, object, text, reasoning)
- Style Score (anime)
- Reasoning Score

### For Chinese (ZH) Benchmark:
```bash
chmod +x run_overall_zh.sh
./run_overall_zh.sh
```

This will evaluate all metrics on the Chinese benchmark, including:
- All categories from EN
- Plus "multilingualism" category

### Individual Metrics:
```bash
./run_alignment.sh   # Alignment only
./run_text.sh        # Text only  
./run_diversity.sh   # Diversity only
./run_style.sh       # Style only
./run_reasoning.sh   # Reasoning only
```

(Note: You may need to update these individual scripts with the new IMAGE_DIR and MODEL_NAMES)

## Verification

Run this to verify the structure:
```bash
cd /home/bpan/OneIG-Benchmark
ls -R images_all_models/ | grep -E "^(anime|human|object|text|reasoning|multilingualism)/$" -A 3
```

Check image counts:
```bash
for cat in anime human object text reasoning multilingualism; do
  for model in omni omni-ep; do
    if [ -d "images_all_models/$cat/$model" ]; then
      count=$(ls images_all_models/$cat/$model/*.webp 2>/dev/null | wc -l)
      echo "$cat/$model: $count images"
    fi
  done
done
```

## Key Files

| File | Purpose |
|------|---------|
| `OneIG-Bench.csv` | English benchmark (1,120 prompts) |
| `OneIG-Bench-ZH.csv` | Chinese benchmark (1,320 prompts) |
| `reorganize_by_index.py` | Reorganization script (run once for new images) |
| `run_all_tests.sh` | **Main script** - runs both EN & ZH with logging |
| `run_overall.sh` | EN evaluation only |
| `run_overall_zh.sh` | ZH evaluation only |
| `run_style.sh` | Style score standalone test |
| `images_all_models/` | Reorganized images directory |

## Notes

1. **Symlinks**: Images are symlinked to original locations in `/weka/cedric/` to save space
2. **Image Format**: Files are named `.webp` but are actually PNG files (symlinked from `image.png`)
3. **Benchmark Differences**: ZH benchmark has 200 more prompts than EN (1,320 vs 1,120)
4. **Model Naming**: Script automatically detects `omni-ep` if directory name contains "_ep_" or "ep_cfg"

## Troubleshooting

If evaluations can't find images, verify symlinks work:
```bash
ls -la images_all_models/anime/omni/000.webp
readlink images_all_models/anime/omni/000.webp
```

If symlinks are broken, regenerate with copies:
```bash
python3 reorganize_by_index.py \
  --source_dirs "/weka/cedric/exp_32b_stage_2_0_qwen_vl_ckpt=15000_oneig_bench_en_cfg=3.5_omni_exp_32b_stage_2_0" \
                "/weka/cedric/exp_32b_stage_2_0_qwen_vl_ckpt=15000_oneig_bench_en_ep_cfg=3.5_omni_exp_32b_stage_2_0" \
                "/weka/cedric/exp_32b_stage_2_0_qwen_vl_ckpt=15000_oneig_bench_zh_cfg=3.5_omni_exp_32b_stage_2_0" \
                "/weka/cedric/exp_32b_stage_2_0_qwen_vl_ckpt=15000_oneig_bench_zh_ep_cfg=3.5_omni_exp_32b_stage_2_0" \
  --output_dir "/home/bpan/OneIG-Benchmark/images_all_models" \
  --benchmark_dir "/home/bpan/OneIG-Benchmark" \
  --copy
```

