# Create or Open Draft

You are helping the user create a new draft exploration spec or continue working on an existing one.

## Command Formats

```bash
# Create from idea
/planning-draft IDEA-001

# Create new draft (interactive)
/planning-draft

# Open existing draft
/planning-draft advanced_caching

# Add session log entry to current draft
/planning-draft --log "Benchmarked queries - 50ms avg"
```

## Your Task

Parse the command arguments to determine the operation:

1. **IDEA-NNN** → Create draft from existing idea
2. **{draft_slug}** → Open existing draft by name
3. **--log "text"** → Add log entry to active draft
4. **(empty)** → Create new draft interactively

---

## Operation: Create Draft from Idea

### Step 1: Read the Idea

Read `specs/drafts/IDEAS.md` and find the idea by ID (e.g., IDEA-001).
Extract: title, description, tags, created date.

If idea not found:
```
Idea IDEA-{NNN} not found in specs/drafts/IDEAS.md

Available ideas:
[List recent ideas with status=new or status=exploring]

Use: /planning-idea to capture a new idea first
```

### Step 2: Generate Slug

Convert title to slug: lowercase, replace spaces with underscores, remove special chars.
Example: "Advanced Caching Layer" → "advanced_caching_layer"

### Step 3: Create Draft File

Create `specs/drafts/explorations/DRAFT_{slug}.md` with this template:

```markdown
# DRAFT: {Title}

**Draft ID:** {slug}
**Status:** exploring
**Source Idea:** IDEA-{NNN}
**Created:** {ISO timestamp}
**Last Updated:** {ISO timestamp}

---

## Problem

{Description from idea}

## Hypothesis

[What outcome do you expect if this is implemented?]

---

## Exploration Notes

### Option A: [First approach]

- Pros:
- Cons:
- Good for:

### Option B: [Second approach]

- Pros:
- Cons:
- Good for:

---

## Questions to Answer

- [ ] [First question to research]
- [ ] [Second question]
- [ ] [Third question]

## Research Done

- [ ] [First research item]

---

## Potential Home

**If promoted, this would likely become:**

- **Type:** Unknown (Feature / Epic / Enhancement)
- **Milestone:** Unknown
- **Epic:** Unknown
- **Rationale:** [Why this placement makes sense]

---

## Decision Criteria for Promotion

- [ ] Clear problem statement with data
- [ ] Chosen approach (not still exploring options)
- [ ] Estimated effort (small/medium/large)
- [ ] Dependencies identified
- [ ] No blocking questions remaining

---

## Session Log

### {Today's Date} - Initial exploration

- Created draft from IDEA-{NNN}
- [Add notes as you explore]

---
```

### Step 4: Update Drafts Index

Read `specs/drafts/.drafts_index.json` and add:

```json
{
  "draft_id": "{slug}",
  "file": "explorations/DRAFT_{slug}.md",
  "status": "exploring",
  "created": "{ISO timestamp}",
  "last_updated": "{ISO timestamp}",
  "source_idea": "IDEA-{NNN}",
  "tags": [{tags from idea}],
  "potential_home": {
    "type": "unknown",
    "milestone": null,
    "epic": null
  },
  "time_spent_minutes": 0,
  "session_started": "{ISO timestamp}"
}
```

Set `active_draft` to this draft's ID.

### Step 5: Update Idea Status

In `specs/drafts/IDEAS.md`, update the idea's status from `new` to `draft_created`.

### Step 6: Display Confirmation

```
Draft created: {Title}

Location: specs/drafts/explorations/DRAFT_{slug}.md
Source: IDEA-{NNN}
Status: exploring

Quick Reference:
[Show first 30 lines of the draft]

Suggested Next Steps:
1. Fill in the "Hypothesis" section
2. List 2-3 approach options
3. Add questions to research
4. When ready: /planning-promote {slug}

Commands:
- Add session log: /planning-draft --log "notes"
- View all drafts: /planning-drafts
- Promote: /planning-promote {slug}
```

---

## Operation: Create New Draft (Interactive)

If no arguments provided, use AskUserQuestion:

### Question 1: Title

- Question: "What's the draft title? (e.g., 'Advanced Caching Layer')"
- Header: "Title"
- Options:
  - label: "Caching Strategy", description: "Performance optimization"
  - label: "API Enhancement", description: "New endpoints or changes"
  - label: "Data Pipeline", description: "Processing or ETL"
  - (User selects "Other" for custom)

### Question 2: Problem Statement

- Question: "What problem does this solve? (1-2 sentences)"
- Header: "Problem"
- Options:
  - label: "Performance bottleneck", description: "Something is too slow"
  - label: "Missing functionality", description: "Need new capability"
  - label: "Technical debt", description: "Existing code needs improvement"
  - (User selects "Other" for custom)

### Question 3: Potential Type

- Question: "What type of work might this become?"
- Header: "Type"
- Options:
  - label: "Feature", description: "Single implementation unit (1-2 weeks)"
  - label: "Epic", description: "Multi-feature initiative (3+ weeks)"
  - label: "Enhancement", description: "Modify existing feature"
  - label: "Unknown", description: "Still exploring"

Then create the draft file and index entry as above (without source_idea).

---

## Operation: Open Existing Draft

### Step 1: Find Draft

Read `specs/drafts/.drafts_index.json` and find by draft_id matching the argument.

If not found, search for partial match or list available drafts:

```
Draft '{name}' not found.

Available drafts:
- advanced_caching (exploring) - 45m spent
- realtime_validation (new) - 0m spent

Use: /planning-draft {name}
```

### Step 2: Set Active and Load

Update `active_draft` in the index.
Reset `session_started` to current timestamp.

### Step 3: Display Context

```
Switched to draft: {Title}

Status: {status}
Time spent: {time_spent_minutes}m
Source: {source_idea or "Created directly"}

Current State:
[Show key sections: Problem, current approach if decided, open questions]

Session Log (recent):
[Show last 3 session log entries]

Commands:
- Add log: /planning-draft --log "notes"
- Promote: /planning-promote {slug}
- Switch: /planning-draft {other_slug}
```

---

## Operation: Add Session Log

If `--log "text"` is provided:

### Step 1: Find Active Draft

Read `specs/drafts/.drafts_index.json` to get `active_draft`.
If no active draft:
```
No active draft. Use /planning-draft {name} to open one first.
```

### Step 2: Append to Session Log

Read the draft file and append to the Session Log section:

```markdown
### {Today's Date} - {Time}

- {log text}
```

If today's date header already exists, just append the bullet point.

### Step 3: Update Timestamps

Update `last_updated` in both the draft file and index.
Calculate time spent: `time_spent_minutes += (now - session_started)`.
Reset `session_started = now`.

### Step 4: Confirm

```
Added to session log: "{text}"

Draft: {title}
Time this session: {session_minutes}m
Total time: {total_minutes}m
```

---

## Important Notes

- Draft slugs should be lowercase with underscores (snake_case)
- Always update both the draft file AND the index
- Time tracking is automatic via session_started
- The index is gitignored; draft files are tracked
- Keep session log entries concise (1-2 lines each)
