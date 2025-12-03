# Planning Commands - Quick Reference

## Available Commands

All commands are located in `.claude/planning/`

### Core Commands (Implementation Tracking)

1. **`/planning/resume`** - Restore context after /clear
   - Loads active feature checkpoint AND brainstorming state
   - Shows current phase, tasks, drafts, and session notes
   - Minimal context (< 500 lines, < 10 seconds)
   - **Use this FIRST after every /clear**

2. **`/planning/status`** - Quick feature orientation
   - Shows current feature, phase, progress
   - Lists epic and milestone
   - Shows blockers if any
   - Fast execution (< 3 seconds)

3. **`/planning/progress`** - Project-wide dashboard
   - Runs parse_checkpoints.py
   - Shows all milestones, epics, features
   - Progress percentages at all levels
   - Time tracking summary

4. **`/planning/checkpoint`** - Update progress
   - Multiple flags for different operations
   - Automatic time tracking
   - Atomic writes (corruption-safe)

### Brainstorming Commands (NEW)

5. **`/planning/idea`** - Quick idea capture (< 5 seconds)
   - Append to IDEAS.md log
   - Auto-generates unique ID
   - Optional tags

6. **`/planning/draft`** - Create/open exploration spec
   - Create from idea: `/planning/draft IDEA-001`
   - Create new: `/planning/draft`
   - Open existing: `/planning/draft {name}`
   - Add log: `/planning/draft --log "notes"`

7. **`/planning/drafts`** - List all drafts
   - Shows active draft, all drafts, idea counts
   - Quick overview of exploration pipeline

8. **`/planning/promote`** - Convert draft → epic/feature
   - Guided decision framework
   - Creates feature or epic spec
   - Updates source status

9. **`/planning/session-notes`** - Session scratch management
   - View: `/planning/session-notes`
   - Add note: `/planning/session-notes --add "note"`
   - Set context: `/planning/session-notes --context "focus"`
   - Park item: `/planning/session-notes --park "reminder"`
   - Clear: `/planning/session-notes --clear`

10. **`/planning/brainstorm`** - Interactive exploration session
    - New topic: `/planning/brainstorm <topic>`
    - Resume: `/planning/brainstorm --continue`
    - Save to draft: `/planning/brainstorm --save`
    - Feature focus: `/planning/brainstorm --feature <name>`
    - Epic focus: `/planning/brainstorm --epic <name>`

### Scaffolding Commands

11. **`/planning/new-feature`** - Create feature from template
12. **`/planning/new-epic`** - Create epic from template
13. **`/planning/new-milestone`** - Create milestone from template
14. **`/planning/goto-feature`** - Switch feature contexts

## Checkpoint Command Flags

```bash
# Mark task complete
/planning/checkpoint --complete-task "Task description"

# Move to next phase
/planning/checkpoint --next-phase

# Start specific phase
/planning/checkpoint --start-phase N

# Add blocker
/planning/checkpoint --add-blocker "Blocker description"

# Remove blocker
/planning/checkpoint --remove-blocker "Blocker description"

# Update notes
/planning/checkpoint --update-note "Note text"

# Complete feature
/planning/checkpoint --complete-feature
```

## File Locations

### Implementation Tracking

- Slash commands: `.claude/planning/*.md`
- Test scripts: `scripts/test_checkpoint_commands.py`
- Progress parser: `scripts/parse_checkpoints.py`
- Active feature pointer: `specs/.checkpoints/current.json`
- Feature checkpoints: `specs/milestones/.../features/*/.checkpoint`

### Brainstorming (NEW)

- Ideas log: `specs/drafts/IDEAS.md` (git tracked)
- Draft specs: `specs/drafts/explorations/DRAFT_*.md` (git tracked)
- Session notes: `specs/drafts/.session_notes` (gitignored)
- Drafts index: `specs/drafts/.drafts_index.json` (gitignored)

## Typical Workflows

### Implementation Flow

1. Start session → `/planning/resume`
2. Work on tasks
3. Complete task → `/planning/checkpoint --complete-task "..."`
4. Finish phase → `/planning/checkpoint --next-phase`
5. Hit `/clear` to reset conversation
6. Resume → `/planning/resume`

### Brainstorming Flow

1. Capture idea → `/planning/idea <description>`
2. Explore as draft → `/planning/draft IDEA-NNN`
3. Research and take notes → `/planning/session-notes --add "note"`
4. When ready → `/planning/promote {draft}`
5. Start implementation → `/planning/goto-feature {name}`

### Combined Flow (Typical Day)

```bash
# After /clear - restore everything
/planning/resume

# Continue implementation
/planning/checkpoint --complete-task "Implement cache layer"

# Tangential idea during work
/planning/idea Add Redis support for distributed caching

# Back to implementation
/planning/checkpoint --next-phase

# End of day - check progress
/planning/progress
```

## Git Strategy

**Tracked (shared):**

- `specs/drafts/IDEAS.md` - Shared idea log
- `specs/drafts/explorations/DRAFT_*.md` - Draft specs

**Gitignored (personal state):**

- `specs/.checkpoints/` - Feature progress state
- `specs/**/.checkpoint` - Individual checkpoints
- `specs/drafts/.session_notes` - Session scratch
- `specs/drafts/.drafts_index.json` - Draft registry

## Success Indicators

- 14 slash commands available
- Automatic time tracking working
- Progress calculation accurate
- Atomic checkpoint writes
- Brainstorming state survives /clear
- Ideas → Drafts → Features pipeline functional

## Troubleshooting

**Commands not recognized:**

- Commands are in `.claude/planning/`, not `~/.claude/commands/`
- Ensure files have `.md` extension
- Check command syntax matches filename

**Checkpoint corrupted:**

- Atomic writes prevent this
- Check .tmp files in feature directory
- Restore from git if needed (checkpoints are gitignored)

**Brainstorming files missing:**

- Run a brainstorming command to initialize
- Check `specs/drafts/` directory exists
- Verify .gitignore entries are correct

**Progress not updating:**

- Verify checkpoint file syntax (YAML)
- Run `python scripts/parse_checkpoints.py` manually
- Check file permissions

## Command Summary Table

| Command | Purpose | Time |
|---------|---------|------|
| `/planning/resume` | Restore all context after /clear | < 10s |
| `/planning/status` | Quick feature status | < 3s |
| `/planning/progress` | Project dashboard | < 10s |
| `/planning/checkpoint` | Update feature progress | < 5s |
| `/planning/idea` | Quick idea capture | < 5s |
| `/planning/draft` | Create/open draft | < 30s |
| `/planning/drafts` | List all drafts | < 3s |
| `/planning/promote` | Draft → epic/feature | 1-2 min |
| `/planning/session-notes` | Session scratch | < 5s |
| `/planning/brainstorm` | Interactive exploration | varies |
| `/planning/new-feature` | Scaffold feature | < 2 min |
| `/planning/new-epic` | Scaffold epic | < 2 min |
| `/planning/goto-feature` | Switch context | < 5s |

---

## Command Reference (Glossary)

### `/planning/idea`

Capture a rough idea to IDEAS.md for later exploration.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<description>` | Yes | The idea text to capture |

**Behavior:**

- Assigns auto-incrementing ID (IDEA-001, IDEA-002, etc.)
- Timestamps the entry
- Sets status to `new`

**Example:** `/planning/idea Add real-time validation feedback via WebSockets`

### `/planning/draft`

Create or open a draft exploration document.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<id\|name>` | Yes | Either `IDEA-NNN` to link to existing idea, or descriptive name |

**Behavior:**

- Creates `DRAFT_<name>.md` in `specs/drafts/explorations/`
- Updates `.drafts_index.json` with draft metadata
- If linked to IDEA, updates idea status to `drafting`
- Opens existing draft if already created

**Example:** `/planning/draft IDEA-001` or `/planning/draft advanced_caching`

### `/planning/drafts`

Display dashboard of all captured ideas and draft explorations.

**Parameters:** None

**Behavior:**

- Parses IDEAS.md for all idea entries
- Reads `.drafts_index.json` for draft status
- Shows tabular view with status, ID, summary, dates
- Indicates active draft

### `/planning/promote`

Promote a validated draft to formal epic or feature.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<draft>` | Yes | Draft ID (e.g., `DRAFT_advanced_caching` or just `advanced_caching`) |

**Behavior:**

- Validates promotion criteria checklist
- Prompts for target placement:
  - **A)** New Epic under milestone
  - **B)** New Feature under epic
  - **C)** Enhancement to existing feature
- Creates IMPLEMENTATION.md, TASKS.md, .checkpoint
- Updates draft and linked idea status to `promoted`

**Example:** `/planning/promote advanced_caching`

### `/planning/session-notes`

Manage ephemeral session scratch notes (gitignored).

| Parameter | Required | Description |
|-----------|----------|-------------|
| (none) | - | Display current session notes |
| `--add <note>` | - | Add a scratch note |
| `--context <focus>` | - | Set active context/focus |
| `--park <item>` | - | Add to parking lot (don't forget) |
| `--file <path>` | - | Track file being explored |
| `--clear` | - | Reset all session notes |

**Behavior:**

- Reads/writes `.session_notes` YAML file
- Timestamps all updates
- Notes persist until cleared or session ends

**Example:** `/planning/session-notes --add "FastAPI has native WebSocket support"`

### `/planning/brainstorm`

Start interactive brainstorming session with guided exploration.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<topic>` | - | Start new brainstorm on topic |
| `--continue` | - | Resume active brainstorm from session notes |
| `--save` | - | Save session notes to active draft |
| `--feature <name>` | - | Brainstorm modifications to existing feature |
| `--epic <name>` | - | Brainstorm new features for existing epic |

**Behavior:**

- Searches codebase for relevant context
- Presents structured exploration options
- Captures insights to session notes automatically
- Enables live plan modification with confirmation

**Example:** `/planning/brainstorm real-time validation feedback`

### Status Values

**Ideas:** `new` → `drafting` → `promoted` | `archived`

**Drafts:** `exploring` → `ready` → `promoted` | `archived`

**Features:** `not_started` → `in_progress` → `completed` | `blocked`
