---
name: output-truncate
description: |
  Truncate tool outputs to prevent token bloat and context overflow.
  
  USE WHEN:
  - Tool output exceeds 1000 tokens
  - web_fetch returns HTML/error pages
  - exec commands return large directory listings
  - read returns large files
  - You need to keep context window manageable
  
  DON'T USE WHEN:
  - Full output is required for the task
  - Processing binary data
  - Output is already small (< 500 tokens)
  - You need exact character positions
  
  OUTPUTS: Truncated text with indicator showing how much was removed
  TOOLS: Python script with per-tool-type limits
---

# Output Truncation Utility

Prevent tool output from consuming excessive tokens.

## Quick Start

```bash
# Truncate web_fetch output
python3 skills/output_truncate.py web_fetch /tmp/web_output.txt

# Truncate exec output with custom limit
python3 skills/output_truncate.py exec /tmp/command_output.txt 500

# Truncate read output
python3 skills/output_truncate.py read /tmp/large_file.txt 1000
```

## Default Limits

| Tool | Max Tokens | Strategy |
|------|------------|----------|
| web_fetch | 1,000 | Detect error pages, extract text |
| exec | 500 | Truncate long listings (ls, find) |
| read | 1,000 | Show first/last for large files |
| browser | 2,000 | Truncate DOM snapshots |
| web_search | 1,000 | Truncate search results |

## Usage in Workflows

```bash
# Instead of using raw output
curl -s https://example.com > /tmp/output.txt
python3 skills/output_truncate.py web_fetch /tmp/output.txt > /tmp/truncated.txt
# Use /tmp/truncated.txt in context
```

## Integration

Add to skill scripts that produce large outputs:

```python
import sys
sys.path.insert(0, 'skills')
from output_truncate import truncate_output

large_output = get_tool_output()
truncated = truncate_output(large_output, max_tokens=1000, tool_name="my_tool")
```
