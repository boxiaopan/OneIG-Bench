#!/bin/bash

# Run both EN and ZH evaluations sequentially with proper logging

# Create logs directory if it doesn't exist
mkdir -p logs

# Generate timestamp for log files
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
EN_LOG="logs/eval_EN_${TIMESTAMP}.log"
ZH_LOG="logs/eval_ZH_${TIMESTAMP}.log"
SUMMARY_LOG="logs/summary_${TIMESTAMP}.log"

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║           Running OneIG-Bench Evaluations (EN + ZH)                        ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Started at: $(date)"
echo "Logs will be saved to:"
echo "  - English: $EN_LOG"
echo "  - Chinese: $ZH_LOG"
echo "  - Summary: $SUMMARY_LOG"
echo ""

# Start overall timer
overall_start=$(date +%s)

# Save configuration to summary
{
    echo "OneIG-Bench Evaluation Summary"
    echo "=============================="
    echo "Started: $(date)"
    echo ""
    echo "Configuration:"
    echo "  IMAGE_DIR: /home/bpan/OneIG-Benchmark/organized_images"
    echo "  IMAGE_TYPE: non-grids (configurable in run_overall*.sh)"
    echo "  CHECKPOINT: 15000 (configurable in run_overall*.sh)"
    echo "  MODELS: omni, omni-ep"
    echo "  IMAGE_GRID: 1 (single images)"
    echo ""
    echo "Directory Structure:"
    echo "  organized_images/MODEL/IMAGE_TYPE/CHECKPOINT/LANGUAGE/CATEGORY/"
    echo ""
} > "$SUMMARY_LOG"

# Run English evaluation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1/2 - Running ENGLISH evaluation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
en_start=$(date +%s)

if ./run_overall.sh 2>&1 | tee "$EN_LOG"; then
    en_end=$(date +%s)
    en_duration=$((en_end - en_start))
    echo "✅ English evaluation completed in $en_duration seconds"
    echo ""
    
    {
        echo "English Evaluation: SUCCESS"
        echo "  Duration: $en_duration seconds"
        echo "  Log: $EN_LOG"
        echo ""
    } >> "$SUMMARY_LOG"
else
    en_end=$(date +%s)
    en_duration=$((en_end - en_start))
    echo "❌ English evaluation failed after $en_duration seconds"
    echo "   Check log: $EN_LOG"
    echo ""
    
    {
        echo "English Evaluation: FAILED"
        echo "  Duration: $en_duration seconds"
        echo "  Log: $EN_LOG"
        echo "  Error: Check log file for details"
        echo ""
    } >> "$SUMMARY_LOG"
fi

# Run Chinese evaluation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2/2 - Running CHINESE evaluation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
zh_start=$(date +%s)

if ./run_overall_zh.sh 2>&1 | tee "$ZH_LOG"; then
    zh_end=$(date +%s)
    zh_duration=$((zh_end - zh_start))
    echo "✅ Chinese evaluation completed in $zh_duration seconds"
    echo ""
    
    {
        echo "Chinese Evaluation: SUCCESS"
        echo "  Duration: $zh_duration seconds"
        echo "  Log: $ZH_LOG"
        echo ""
    } >> "$SUMMARY_LOG"
else
    zh_end=$(date +%s)
    zh_duration=$((zh_end - zh_start))
    echo "❌ Chinese evaluation failed after $zh_duration seconds"
    echo "   Check log: $ZH_LOG"
    echo ""
    
    {
        echo "Chinese Evaluation: FAILED"
        echo "  Duration: $zh_duration seconds"
        echo "  Log: $ZH_LOG"
        echo "  Error: Check log file for details"
        echo ""
    } >> "$SUMMARY_LOG"
fi

# Calculate total time
overall_end=$(date +%s)
overall_duration=$((overall_end - overall_start))
overall_hours=$((overall_duration / 3600))
overall_mins=$(((overall_duration % 3600) / 60))
overall_secs=$((overall_duration % 60))

# Final summary
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                        ALL EVALUATIONS COMPLETE                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Completed at: $(date)"
echo "Total Duration: ${overall_hours}h ${overall_mins}m ${overall_secs}s"
echo ""
echo "Results saved to:"
echo "  📊 Results:  ./results/"
echo "  📄 EN Log:   $EN_LOG"
echo "  📄 ZH Log:   $ZH_LOG"
echo "  📝 Summary:  $SUMMARY_LOG"
echo ""

{
    echo "=============================="
    echo "Completed: $(date)"
    echo "Total Duration: ${overall_hours}h ${overall_mins}m ${overall_secs}s"
    echo ""
    echo "Results Directory: ./results/"
    echo "EN Log: $EN_LOG"
    echo "ZH Log: $ZH_LOG"
} >> "$SUMMARY_LOG"

# Display result files if they exist
if [ -d "results" ]; then
    echo "Result files generated:"
    ls -lh results/*${TIMESTAMP:0:10}* 2>/dev/null || ls -lh results/*.csv 2>/dev/null | tail -20
fi

echo ""
echo "To view logs:"
echo "  cat $EN_LOG"
echo "  cat $ZH_LOG"
echo "  cat $SUMMARY_LOG"
echo ""




