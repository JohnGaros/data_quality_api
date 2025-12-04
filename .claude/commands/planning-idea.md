# Capture New Idea

You are helping the user quickly capture a new idea to the IDEAS.md log.

## Your Task

1. Parse the idea description from command arguments (everything after `/planning-idea`)
2. If no description provided, ask for it using AskUserQuestion
3. Read `specs/drafts/IDEAS.md` to find the next IDEA-NNN ID
4. Generate today's date section if not present
5. Append the new idea in the standard format
6. Confirm capture with next steps

## Step-by-Step Instructions

### Step 1: Get Idea Description

The command format is: `/planning-idea <description>`

If description is provided (non-empty after command):
- Use it directly
- Extract a title from the first sentence (first 50 chars or up to first period)

If no description provided:
- Use AskUserQuestion to prompt:
  - Question: "What's the idea? (1-2 sentences describing the concept)"
  - Header: "Idea"
  - Options: Provide 2-3 example formats, let user select "Other" for custom

### Step 2: Parse Next ID

Read `specs/drafts/IDEAS.md` and find the comment `<!-- Next ID: IDEA-NNN -->`.
Extract NNN and use it for the new idea. After appending, update the comment to increment.

If no Next ID comment found, scan for highest existing IDEA-NNN and use NNN+1.

### Step 3: Optional Tags

Use AskUserQuestion to offer common tags:

- Question: "Add tags? (helps with filtering later)"
- Header: "Tags"
- Options:
  - label: "performance", description: "Speed, caching, optimization"
  - label: "api", description: "REST endpoints, integrations"
  - label: "infrastructure", description: "Storage, compute, deployment"
  - label: "Skip tags", description: "Add tags later if needed"
- multiSelect: true

### Step 4: Get Today's Date Section

Check if today's date (YYYY-MM-DD format) section exists in IDEAS.md.
If not, create it after the header section.

### Step 5: Append Idea

Append this format to IDEAS.md under today's date section:

```markdown
### [IDEA-{NNN}] {Title}

**Status:** new
**Tags:** {tags or "untagged"}
**Created:** {ISO timestamp}

{Full description}

---
```

### Step 6: Update Next ID Comment

Update `<!-- Next ID: IDEA-NNN -->` to increment the number.

### Step 7: Confirm

Display:

```
Captured: IDEA-{NNN} - {Title}

Location: specs/drafts/IDEAS.md

Next steps:
- Explore further: /planning-draft IDEA-{NNN}
- View all ideas: Read specs/drafts/IDEAS.md
- Promote directly: /planning-promote IDEA-{NNN}
```

## Example Usage

```bash
# With inline description
/planning-idea Add caching for catalog lookups to reduce DB load

# Interactive (no description)
/planning-idea
```

## Important Notes

- Keep it fast (< 5 seconds for inline, < 15 seconds interactive)
- Title should be concise (< 60 chars)
- Description can be longer (1-3 sentences is ideal)
- Always update the Next ID comment to prevent duplicates
- Use ISO 8601 timestamps (YYYY-MM-DDTHH:MM:SSZ)
