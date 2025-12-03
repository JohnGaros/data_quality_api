# Interactive Brainstorming Session

Start an interactive brainstorming session for exploring ideas, features, or architectural decisions.

## Arguments

$ARGUMENTS = Topic or context for brainstorming:
- `<topic>` - Start new brainstorm on topic
- `--continue` - Resume active brainstorm from session notes
- `--save` - Save session notes to active draft
- `--feature <name>` - Brainstorm modifications to existing feature
- `--epic <name>` - Brainstorm new features for existing epic

## Instructions

### New Brainstorm Session (`<topic>`)

1. **Initialize session** in `.session_notes`:
   ```yaml
   session_id: "brainstorm-<timestamp>"
   active_context: "Brainstorming: <topic>"
   ```

2. **Set up brainstorm context:**
   - If topic relates to existing code, search codebase for relevant files
   - If topic relates to existing planning, load relevant specs
   - Track explored files in `exploring_files`

3. **Enter brainstorm mode** with structured exploration:
   ```
   ================================================================================
   BRAINSTORM SESSION: <topic>
   ================================================================================
   Session ID: brainstorm-2025-12-03-1430

   Let's explore this idea together. I'll help you think through:
   - Problem definition
   - Possible approaches
   - Trade-offs and considerations
   - Integration with existing architecture

   Current context loaded:
   - [list relevant files/specs found]

   ──────────────────────────────────────────────────────────────────────────────────
   What aspect would you like to explore first?

   A) Define the problem this solves
   B) Explore technical approaches
   C) Review related existing code
   D) Discuss integration points
   E) Free-form exploration

   Or just start talking and I'll follow your lead.
   ================================================================================
   ```

4. **During brainstorm:**
   - Actively capture insights to session notes
   - Suggest relevant code to explore
   - Ask clarifying questions
   - Propose alternatives and trade-offs
   - Track action items in parking lot

### Continue Session (`--continue`)

1. Read `.session_notes`
2. Display current state
3. Resume from where left off

### Save to Draft (`--save`)

1. Read current session notes
2. If active draft exists, append to its Research Notes section
3. If no active draft:
   - Ask if should create new draft
   - Prompt for draft name
   - Create draft with session content

### Feature Brainstorm (`--feature <name>`)

1. Load feature's IMPLEMENTATION.md and TASKS.md
2. Set context to feature modification
3. Present options:
   ```
   Brainstorming modifications to: <feature_name>

   Current state:
   - Phase: 3 of 7
   - Status: in_progress

   What would you like to explore?

   A) Add new tasks to current phase
   B) Add new phase
   C) Modify approach for existing task
   D) Discuss blockers or alternatives
   E) Re-scope feature requirements
   ```

### Epic Brainstorm (`--epic <name>`)

1. Load epic's EPIC.md and existing features
2. Set context to epic expansion
3. Present options:
   ```
   Brainstorming for epic: <epic_name>

   Existing features:
   - feature_1 (completed)
   - feature_2 (in_progress)
   - feature_3 (planned)

   What would you like to explore?

   A) Propose new feature for this epic
   B) Re-prioritize existing features
   C) Discuss cross-feature dependencies
   D) Scope adjustment (add/remove features)
   ```

## Live Plan Modification

During brainstorming, the following modifications can be made in real-time:

### Modifying Ideas (IDEAS.md)
- Add new ideas with `/planning/idea`
- Update status of existing ideas
- Add tags or links to related concepts

### Modifying Drafts
- Update problem statement
- Add research notes
- Answer key questions
- Update technical considerations

### Modifying Features (requires confirmation)
- Add tasks to TASKS.md
- Update IMPLEMENTATION.md approach
- Add blockers to .checkpoint
- Adjust phase scope

### Modifying Epics (requires confirmation)
- Add planned features
- Update epic scope in EPIC.md
- Re-prioritize feature order

## Brainstorm Output Integration

At end of session (or with `--save`):

```
Session Summary
═══════════════════════════════════════════════════════════════════════════════

Key Insights:
1. <insight 1>
2. <insight 2>
3. <insight 3>

Action Items:
- [ ] <action 1>
- [ ] <action 2>

Files Explored:
- src/dq_api/routes/validation.py
- src/dq_core/engine/rule_engine.py

Save Options:
A) Create new idea in IDEAS.md
B) Create new draft exploration
C) Add to existing draft: DRAFT_<name>
D) Add tasks to feature: <feature_name>
E) Discard session notes

Select [A/B/C/D/E]:
```

## Example Flow

```
User: /planning/brainstorm real-time validation feedback

Claude: [Searches codebase, finds relevant files]
        [Presents brainstorm session intro]

User: Let's explore WebSocket vs SSE approaches

Claude: [Discusses trade-offs]
        [Adds notes to session]
        [Suggests relevant code to review]

User: I like the WebSocket approach. What would integration look like?

Claude: [Explores integration points]
        [Parks action item: "Check Azure SignalR"]
        [Updates session context]

User: /planning/brainstorm --save

Claude: [Presents summary]
        [Creates draft or adds to existing]
        [Links to IDEAS.md if applicable]
```
