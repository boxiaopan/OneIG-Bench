#!/bin/bash

# start_time
start_time=$(date +%s)

# mode (EN/ZH)
MODE=ZH

# image_root_dir
# Reorganized directory with expected category/model structure:
IMAGE_DIR="/home/bpan/OneIG-Benchmark/images_all_models"

# model list - now includes both omni and omni-ep variants
MODEL_NAMES=("omni" "omni-ep")

# image grid (one value per model) - 1 means single image, not a grid
IMAGE_GRID=(1 1)

echo "Running all evaluation scripts (ZH mode)"

# pip install transformers==4.50.0

# Alignment Score

echo "It's alignment time."

python -m scripts.alignment.alignment_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \
  --class_items "anime" "human" "object" "multilingualism" \

# Text Score

echo "It's text time."

python -m scripts.text.text_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR/text" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \

# Diversity Score

echo "It's diversity time."

python -m scripts.diversity.diversity_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \
  --class_items "anime" "human" "object" "text" "reasoning" "multilingualism" \

# Style Score

echo "It's style time."

python -m scripts.style.style_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR/anime" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \

# Reasoning Score

echo "It's reasoning time."

python -m scripts.reasoning.reasoning_score \
  --mode "$MODE" \
  --image_dirname "${IMAGE_DIR}/reasoning" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \


rm -rf tmp_*
# end_time
end_time=$(date +%s)
duration=$((end_time - start_time))

echo "✅ All evaluations finished in $duration seconds."

