#!/bin/bash

# start_time
start_time=$(date +%s)

# mode (EN/ZH)
MODE=EN

# Base image directory (new organized structure)
IMAGE_DIR="/home/bpan/OneIG-Benchmark/organized_images"

# Image type: "grids" for 2x2 grid images, "non-grids" for single images
IMAGE_TYPE="non-grids"

# Checkpoint number
CHECKPOINT="15000"

# model list
MODEL_NAMES=("omni" "omni-ep")

# image grid (one value per model) - 1 means single image, 2 means 2x2 grid
IMAGE_GRID=(1 1)

# Reasoning Score

echo "It's reasoning time."

python -m scripts.reasoning.reasoning_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR" \
  --image_type "$IMAGE_TYPE" \
  --checkpoint "$CHECKPOINT" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \

rm -rf tmp_*
# end_time
end_time=$(date +%s)
duration=$((end_time - start_time))

echo "✅ Reasoning evaluation finished in $duration seconds."
