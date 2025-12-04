# Promote Draft or Idea

You are helping the user convert a draft exploration or idea into a formal epic or feature specification.

## Command Formats

```bash
# Promote a draft
/planning-promote advanced_caching

# Promote an idea directly
/planning-promote IDEA-001

# Promote with pre-selected destination
/planning-promote advanced_caching --epic E4_OPERATIONS --milestone M3_SCALE_OPERATIONS
```

## Your Task

1. Load the draft or idea content
2. Check promotion readiness (for drafts)
3. Guide through placement decision using the decision framework
4. Create the appropriate spec (feature or epic)
5. Update source status to "promoted"

---

## Step 1: Identify Source

Parse the argument to determine if promoting:
- **Draft:** Argument matches a draft_id in `specs/drafts/.drafts_index.json`
- **Idea:** Argument matches `IDEA-NNN` pattern in `specs/drafts/IDEAS.md`

If neither found:

```
'{argument}' not found as draft or idea.

Available drafts:
{List from .drafts_index.json}

Recent ideas:
{List IDEA-NNN entries with status=new}

Use: /planning-promote {draft_name} or /planning-promote IDEA-NNN
```

---

## Step 2: Load Source Content

### For Draft:

Read `specs/drafts/explorations/DRAFT_{slug}.md` and extract:
- Title (from header)
- Problem statement
- Chosen approach (if decided)
- Potential home (type, milestone, epic)
- Decision criteria checklist
- Questions answered vs unanswered

### For Idea:

Read the idea from `specs/drafts/IDEAS.md` and extract:
- Title
- Description
- Tags
- Created date

---

## Step 3: Promotion Readiness Check (Drafts Only)

For drafts, check the decision criteria:

```markdown
## Decision Criteria for Promotion

- [ ] Clear problem statement with data
- [ ] Chosen approach (not still exploring options)
- [ ] Estimated effort (small/medium/large)
- [ ] Dependencies identified
- [ ] No blocking questions remaining
```

Count checked vs unchecked items.

If < 3 items checked, warn:

```
This draft may not be ready for promotion.

Readiness: {checked}/{total} criteria met

Incomplete:
- [ ] Chosen approach (still has Options A, B, C)
- [ ] 2 blocking questions unanswered

Options:
1. Promote anyway (may need revision later)
2. Continue exploration (recommended)
3. Cancel

What would you like to do?
```

Use AskUserQuestion:
- Question: "Draft has incomplete criteria. How to proceed?"
- Header: "Readiness"
- Options:
  - label: "Promote anyway", description: "Create spec, refine later"
  - label: "Continue exploring", description: "Go back to draft"
  - label: "Cancel", description: "Exit without changes"

If "Continue exploring" → exit with message to use `/planning-draft {slug}`
If "Cancel" → exit with no changes

---

## Step 4: Placement Decision Framework

If `--epic` and `--milestone` flags provided, skip to Step 5.

Otherwise, guide through the decision framework.

### Question 1: Scope Assessment

Use AskUserQuestion:
- Question: "How big is this work?"
- Header: "Scope"
- Options:
  - label: "Small", description: "1-2 days, focused on one area"
  - label: "Medium", description: "1-2 weeks, touches multiple files/modules"
  - label: "Large", description: "2+ weeks, multiple distinct deliverables"
  - label: "Uncertain", description: "Need more exploration"

If "Uncertain" → suggest continuing as draft

### Question 2: Deliverable Structure

Use AskUserQuestion:
- Question: "How many distinct deliverables are there?"
- Header: "Deliverables"
- Options:
  - label: "One", description: "Single cohesive implementation"
  - label: "2-3 related", description: "Few related pieces, one goal"
  - label: "4+ distinct", description: "Multiple separate features"
  - label: "Uncertain", description: "Structure not clear yet"

If "Uncertain" → suggest continuing as draft

### Question 3: Existing Epic Check

First, list existing epics from the project:

Read milestone directories and extract epics:
- M1_MVP_FOUNDATION: E0_CATALOG_FOUNDATION, E1_CORE_VALIDATION, E2_METADATA_LINEAGE
- M2_SECURITY_COMPLIANCE: E3_RBAC_GDPR
- M3_SCALE_OPERATIONS: E4_OPERATIONS

Use AskUserQuestion:
- Question: "Does this fit within an existing epic?"
- Header: "Epic"
- Options:
  - label: "E1_CORE_VALIDATION", description: "Core validation pipeline (M1)"
  - label: "E2_METADATA_LINEAGE", description: "Metadata and lineage (M1)"
  - label: "E3_RBAC_GDPR", description: "Security and compliance (M2)"
  - label: "E4_OPERATIONS", description: "Scale and operations (M3)"
  - label: "New epic needed", description: "Doesn't fit existing structure"

### Decision Matrix

Apply this logic:

| Scope | Deliverables | Existing Epic | Result |
|-------|--------------|---------------|--------|
| Small | One | Yes | Feature in existing epic |
| Small | One | No | Feature (consider new epic) |
| Medium | One | Yes | Feature in existing epic |
| Medium | 2-3 | Yes | Feature (may split later) |
| Medium | 2-3 | No | New epic with features |
| Large | Any | Any | New epic with multiple features |
| Any | 4+ | Any | New epic with multiple features |

Display the recommendation:

```
Based on your answers:
- Scope: {scope}
- Deliverables: {deliverables}
- Existing epic: {epic or "None"}

Recommendation: {Feature in {epic} | New epic in {milestone}}

Proceed with this placement?
```

Use AskUserQuestion to confirm:
- Question: "Create {type} in {location}?"
- Header: "Confirm"
- Options:
  - label: "Yes, create it", description: "Proceed with recommended placement"
  - label: "Choose different location", description: "Override recommendation"
  - label: "Cancel", description: "Exit without creating"

---

## Step 5: Create the Specification

### If Creating Feature in Existing Epic:

1. Determine feature name (slug from draft/idea title)
2. Find epic directory path
3. Create feature directory: `specs/milestones/{M}/epics/{E}/features/{feature}/`
4. Generate IMPLEMENTATION.md from draft content:
   - Copy Problem → Overview
   - Copy chosen approach → Implementation approach
   - Generate phases from draft research items
5. Generate TASKS.md with phases based on draft questions/research
6. Initialize .checkpoint file
7. Update parent EPIC.md to list new feature

### If Creating New Epic:

1. Determine epic name (E{N}_{SLUG})
2. Ask which milestone:

Use AskUserQuestion:
- Question: "Which milestone for this epic?"
- Header: "Milestone"
- Options:
  - label: "M1_MVP_FOUNDATION", description: "MVP phase (Target: 2025-12-30)"
  - label: "M2_SECURITY_COMPLIANCE", description: "Security phase (Target: 2026-01-31)"
  - label: "M3_SCALE_OPERATIONS", description: "Scale phase (Target: 2026-02-28)"

3. Create epic directory: `specs/milestones/{M}/epics/{E}/`
4. Generate EPIC.md from draft content
5. Create features/ subdirectory
6. Optionally create initial feature(s)
7. Update MILESTONE.md

---

## Step 6: Update Source Status

### For Draft:

1. Update draft file: Change `**Status:** exploring` to `**Status:** promoted`
2. Add promotion metadata to draft:

```markdown
---

## Promotion Details

**Promoted to:** {Feature | Epic}
**Location:** {path}
**Date:** {ISO timestamp}
```

3. Update `.drafts_index.json`:
   - Set draft status to "promoted"
   - Add `promoted_to` field

4. If draft had a source idea, update that idea's status to "promoted" in IDEAS.md

### For Idea (direct promotion):

Update the idea in IDEAS.md: Change `**Status:** new` to `**Status:** promoted`
Add a note: `**Promoted to:** {path}`

---

## Step 7: Confirm Creation

Display success message:

```
Promoted: {Title}

**Created:** {Feature in {epic} | New epic {name}}
**Location:** {full path}

**Files created:**
- {IMPLEMENTATION.md | EPIC.md}
- {TASKS.md | features/ directory}
- .checkpoint (initialized)

**Source updated:**
- {Draft/Idea} status → promoted

**Next steps:**
1. Review generated {IMPLEMENTATION.md | EPIC.md}
2. Customize {TASKS.md | add features}
3. Start work: /planning-goto-feature {feature_name}

**Quick commands:**
- View: Read {path}/IMPLEMENTATION.md
- Start: /planning-goto-feature {name}
- Progress: /planning-progress
```

---

## Error Handling

### Draft Not Found

```
Draft '{name}' not found.

Available drafts:
- advanced_caching (exploring)
- realtime_validation (new)

Use: /planning-drafts to see all drafts
```

### Idea Not Found

```
Idea IDEA-{NNN} not found.

Recent ideas:
- IDEA-001: Advanced caching (draft_created)
- IDEA-002: Real-time webhooks (new)

Use: /planning-idea to capture a new idea
```

### Epic Already Exists

```
Epic {name} already exists at {path}.

Options:
1. Create feature within this epic
2. Choose a different epic name
3. Cancel
```

---

## Important Notes

- Promotion is a one-way operation (drafts marked as promoted)
- Generated specs are starting points - user should customize
- Decision framework guides but doesn't force - user can override
- Time tracking carries over from draft to feature checkpoint
- Tags from draft/idea are preserved in feature metadata
- Always update parent documents (EPIC.md, MILESTONE.md) for consistency
