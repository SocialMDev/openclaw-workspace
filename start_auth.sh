#!/bin/bash
# Start Gmail authentication in a tmux session
# This survives connection drops and can be reattached

SESSION_NAME="gmail_auth"

# Kill existing session if any
tmux kill-session -t "$SESSION_NAME" 2>/dev/null

# Create new session
tmux new-session -d -s "$SESSION_NAME" -c /home/faisal/.openclaw/workspace

# Run the authentication script
tmux send-keys -t "$SESSION_NAME" "python3 auth_all.py" Enter

echo "========================================================================"
echo "Gmail Authentication Started in tmux session: $SESSION_NAME"
echo "========================================================================"
echo ""
echo "To attach and monitor progress:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "To detach (keep running in background):"
echo "  Press Ctrl+B, then D"
echo ""
echo "To check if still running:"
echo "  tmux ls"
echo ""
echo "Authentication will wait for you to complete OAuth in browser."
echo "Ports used: 8081-8084 (one per account)"
echo "========================================================================"
