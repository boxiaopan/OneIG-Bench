#!/bin/bash

# start_time
start_time=$(date +%s)

# mode (EN/ZH)
MODE=EN

# Base image directory (new organized structure)
IMAGE_DIR="/home/bpan/OneIG-Benchmark/organized_images"

# Image type: "grids" for 2x2 grid images, "non-grids" for single images
IMAGE_TYPE="grids"
# IMAGE_TYPE="non-grids"

# Checkpoint number
CHECKPOINT="15000"

# model list - now includes both omni and omni-ep variants
MODEL_NAMES=("omni" "omni-ep")

# image grid (one value per model) - 1 means single image, 2 means 2x2 grid
# For grids, use 2; for non-grids, use 1
IMAGE_GRID=(2 2)

echo "Running all evaluation scripts"
echo "  Mode: $MODE"
echo "  Image Dir: $IMAGE_DIR"
echo "  Image Type: $IMAGE_TYPE"
echo "  Checkpoint: $CHECKPOINT"
echo "  Models: ${MODEL_NAMES[*]}"

# Alignment Score

echo "It's alignment time."

python -m scripts.alignment.alignment_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR" \
  --image_type "$IMAGE_TYPE" \
  --checkpoint "$CHECKPOINT" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \
  --class_items "anime" "human" "object" \

# In ZH mode, the class_items list can be extended to include "multilingualism".

# Text Score

echo "It's text time."

python -m scripts.text.text_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR" \
  --image_type "$IMAGE_TYPE" \
  --checkpoint "$CHECKPOINT" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \

# Diversity Score

echo "It's diversity time."

python -m scripts.diversity.diversity_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR" \
  --image_type "$IMAGE_TYPE" \
  --checkpoint "$CHECKPOINT" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \
  --class_items "anime" "human" "object" "text" "reasoning" \

# Style Score

echo "It's style time."

python -m scripts.style.style_score \
  --mode "$MODE" \
  --image_dirname "$IMAGE_DIR" \
  --image_type "$IMAGE_TYPE" \
  --checkpoint "$CHECKPOINT" \
  --model_names "${MODEL_NAMES[@]}" \
  --image_grid "${IMAGE_GRID[@]}" \

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

echo "✅ All evaluations finished in $duration seconds."
