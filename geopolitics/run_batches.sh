#!/bin/bash
# Geopolitics Lectures - Batch Generator
# Runs 6 batches sequentially using OpenClaw gateway API

set -e

OUTPUT_DIR="/home/faisal/.openclaw/workspace/geopolitics"
SOURCE_A="/tmp/source_a.txt"
SOURCE_B="/tmp/source_b.txt"
GATEWAY_URL="http://127.0.0.1:18789"
TOKEN="a4a2ade8a925d89ee760c0f1eadb6df8a679fd4f5387971e"

COMMON_INSTRUCTIONS="Language: Arabic (Modern Standard Arabic), NO diacritics/tashkeel, Markdown headings.
STRICT SOURCE RESTRICTION: Use ONLY the two source files; NO external information.
Citation format: [Source A | Page X].
If info not in sources: Write 'لا أستطيع التحقق من ذلك من المصادر المحملة.'

Per-lecture structure (11 sections):
1. Title: '## محاضرة X: [Title]'
2. Linked CLOs from sources
3. Learning Objectives: 5-7 measurable objectives
4. Deep Outline: 4-6 sections with detailed bullets
5. Glossary: 10-15 terms with definitions
6. Concept Connections: 2 links if supported
7. In-class Activity (goal, steps, minutes, outputs)
8. Discussion Questions: 8-10 questions
9. Formative Quiz: 10 questions with answer key
10. Short Homework
11. What to Study: pages/sections

First read $SOURCE_A and $SOURCE_B completely. Write all output to the specified markdown file. After writing, reply with ANNOUNCE_SKIP."

echo "=== Geopolitics Lecture Generator ==="
echo "Output directory: $OUTPUT_DIR"
echo ""

run_batch() {
    local batch_num=$1
    local lectures=$2
    local topics=$3
    local pages=$4
    local output_file=$5

    echo "[${batch_num}/6] Starting: $lectures..."

    local message="Generate ${lectures} for الجغرافيا السياسية course.
Topics: ${topics}
Source pages: ${pages} from ${SOURCE_A}
${COMMON_INSTRUCTIONS}
Output file: ${output_file}"

    # Use openclaw agent with local mode
    openclaw agent --local -m "$message" --timeout 900 2>&1 | tee "/tmp/batch_${batch_num}.log"

    echo "[${batch_num}/6] Complete. Output: $output_file"
    echo ""

    # Small delay between batches
    sleep 5
}

# Run all 6 batches
run_batch 1 "محاضرة 1, 2, 3" \
    "Introduction to Political Geography, importance, fields of study, historical development" \
    "1-5" \
    "$OUTPUT_DIR/lectures_01-03.md"

run_batch 2 "محاضرة 4, 5" \
    "The State as a Political Geographical Unit - definition, elements, characteristics" \
    "5-11" \
    "$OUTPUT_DIR/lectures_04-05.md"

run_batch 3 "محاضرة 6, 7, 8" \
    "Natural Foundations of the State - location, area, shape" \
    "11-17" \
    "$OUTPUT_DIR/lectures_06-08.md"

run_batch 4 "محاضرة 9, 10" \
    "Human Foundations of the State - population, language, religion" \
    "17-21" \
    "$OUTPUT_DIR/lectures_09-10.md"

run_batch 5 "محاضرة 11, 12" \
    "State Organization, Capital cities, Boundaries and borders, Maritime boundaries" \
    "18-22 and 30-37" \
    "$OUTPUT_DIR/lectures_11-12.md"

run_batch 6 "محاضرة 13, 14" \
    "Types of States and their Development - historical, modern, colonial impact" \
    "25-30" \
    "$OUTPUT_DIR/lectures_13-14.md"

echo "=== All batches complete! ==="
echo ""
echo "Output files:"
ls -lh $OUTPUT_DIR/*.md 2>/dev/null || echo "Check individual batch logs in /tmp/batch_*.log"
