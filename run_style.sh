#!/bin/bash

# start_time
start_time=$(date +%s)

# mode (EN/ZH)
MODE=EN

# image_root_dir
# Reorganized directory with expected category/model structure:
IMAGE_DIR="/home/bpan/OneIG-Benchmark/images_all_models"

# model list - now includes both omni and omni-ep variants
MODEL_NAMES=("omni" "omni-ep")
# model_names=("gpt-4o" "imagen4")

# image grid (one value per model) - 1 means single image, not a grid
IMAGE_GRID=(1 1)

# pip install transformers==4.50.0

# Style Score

echo "It's style time."

python -m scripts.style.style_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR/anime" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \

rm -rf tmp_*
# end_time
end_time=$(date +%s)
duration=$((end_time - start_time))

echo "✅ All evaluations finished in $duration seconds."