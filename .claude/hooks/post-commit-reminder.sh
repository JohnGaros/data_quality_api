#!/bin/bash
# Post-commit reminder hook for Claude Code
# Triggers after git commit to remind Claude to update planning checkpoints

# Read hook input from stdin (JSON with tool_input, tool_response, etc.)
HOOK_INPUT=$(cat)

# Extract the command that was executed
COMMAND=$(echo "$HOOK_INPUT" | jq -r '.tool_input.command // empty')

# Check if it was a git commit command
if [[ "$COMMAND" =~ git\ commit ]] || [[ "$COMMAND" =~ "git add".*"&&".*"git commit" ]]; then
  # Check if the commit was successful by looking at tool_response
  RESPONSE=$(echo "$HOOK_INPUT" | jq -r '.tool_response.stdout // empty')

  # Only show reminder if commit actually succeeded (contains commit hash pattern)
  if [[ "$RESPONSE" =~ \[.*[a-f0-9]+\] ]]; then
    echo ""
    echo "================================================================"
    echo "CHECKPOINT REMINDER"
    echo "================================================================"
    echo "You just committed code. Update the planning checkpoint:"
    echo ""
    echo "  /planning/checkpoint --complete-task \"<task description>\""
    echo ""
    echo "Or if this completes a phase:"
    echo ""
    echo "  /planning/checkpoint --next-phase"
    echo "================================================================"
    echo ""
  fi
fi

exit 0
