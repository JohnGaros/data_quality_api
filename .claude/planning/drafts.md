# List All Drafts

You are showing the user an overview of all drafts and ideas in the exploration pipeline.

## Your Task

1. Read `specs/drafts/.drafts_index.json` for draft information
2. Read `specs/drafts/IDEAS.md` for idea counts by status
3. Display an organized summary

## Step-by-Step Instructions

### Step 1: Read Drafts Index

Read `specs/drafts/.drafts_index.json`.
If file doesn't exist or is empty, show "No drafts yet" message.

Extract for each draft:
- draft_id
- status
- time_spent_minutes
- potential_home.type
- potential_home.epic
- source_idea

Note which draft is `active_draft`.

### Step 2: Read Ideas

Read `specs/drafts/IDEAS.md` and count ideas by status:
- new
- exploring
- draft_created
- promoted
- parked
- rejected

Also extract the 3 most recent ideas with status=new.

### Step 3: Display Summary

Output this format:

```
## Drafts & Ideas Pipeline

### Active Draft

{If active_draft exists:}
-> {draft_id} ({status}) - {time_spent}m spent
   Potential: {type} in {epic or "Unknown"}
   Source: {source_idea or "Created directly"}

{If no active_draft:}
No active draft. Use /planning/draft to create or open one.

---

### All Drafts ({count})

| Draft | Status | Time | Potential Home | Source |
|-------|--------|------|----------------|--------|
| -> {active} | {status} | {time}m | {type}/{epic} | {idea} |
| {draft2} | {status} | {time}m | {type}/{epic} | {idea} |
| {draft3} | {status} | {time}m | {type}/{epic} | {idea} |

{If no drafts:}
No drafts yet. Create one with /planning/draft or /planning/draft IDEA-NNN.

---

### Ideas Summary

| Status | Count |
|--------|-------|
| New | {count} |
| Exploring | {count} |
| Draft Created | {count} |
| Promoted | {count} |
| Parked | {count} |

**Total ideas:** {total}

---

### Recent Ideas (status: new)

{For each of 3 most recent new ideas:}
- IDEA-{NNN}: {title} ({date})

{If no new ideas:}
No new ideas. Capture one with /planning/idea.

---

### Quick Commands

- Capture idea: /planning/idea <description>
- Create draft: /planning/draft
- Open draft: /planning/draft {name}
- Promote: /planning/promote {name}
- View ideas: Read specs/drafts/IDEAS.md
```

## Status Indicators

Use these indicators for draft status:
- `->` for active draft
- `(exploring)` - actively being researched
- `(new)` - just created, not started
- `(ready)` - ready for promotion
- `(parked)` - intentionally deferred

## Empty State

If both drafts and ideas are empty:

```
## Drafts & Ideas Pipeline

No drafts or ideas yet.

Get started:
1. Capture an idea: /planning/idea <description>
2. Or create a draft directly: /planning/draft

The brainstorming pipeline helps you:
- Capture rough ideas quickly
- Explore options before committing
- Promote to features/epics when ready
```

## Important Notes

- Show the active draft prominently at the top
- Time is displayed in minutes for <60m, hours+minutes for longer
- Potential home shows "Unknown" if not yet decided
- Ideas are counted from the markdown file, not a separate index
- Keep output concise - this is a quick overview command
