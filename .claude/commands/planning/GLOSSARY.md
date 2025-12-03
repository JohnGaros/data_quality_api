# Planning Commands Glossary

Quick reference for all planning-related slash commands.

---

## `/planning/idea`

**Function:** Capture a rough idea to IDEAS.md for later exploration.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<description>` | Yes | The idea text to capture |

**Behavior:**
- Assigns auto-incrementing ID (IDEA-001, IDEA-002, etc.)
- Timestamps the entry
- Sets status to `new`

**Example:** `/planning/idea Add real-time validation feedback via WebSockets`

---

## `/planning/draft`

**Function:** Create or open a draft exploration document.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<id\|name>` | Yes | Either `IDEA-NNN` to link to existing idea, or descriptive name |

**Behavior:**
- Creates `DRAFT_<name>.md` in `specs/drafts/explorations/`
- Updates `.drafts_index.json` with draft metadata
- If linked to IDEA, updates idea status to `drafting`
- Opens existing draft if already created

**Example:** `/planning/draft IDEA-001` or `/planning/draft advanced_caching`

---

## `/planning/drafts`

**Function:** Display dashboard of all captured ideas and draft explorations.

**Parameters:** None

**Behavior:**
- Parses IDEAS.md for all idea entries
- Reads `.drafts_index.json` for draft status
- Shows tabular view with status, ID, summary, dates
- Indicates active draft

---

## `/planning/promote`

**Function:** Promote a validated draft to formal epic or feature.

**Parameters:**

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

---

## `/planning/session-notes`

**Function:** Manage ephemeral session scratch notes (gitignored).

**Parameters:**

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

---

## `/planning/brainstorm`

**Function:** Start interactive brainstorming session with guided exploration.

**Parameters:**

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

---

## Related Context Commands

These commands work with the checkpoint system:

| Command | Function |
|---------|----------|
| `/planning/resume` | Restore context after `/clear` |
| `/planning/status` | Show current feature status |
| `/planning/progress` | View project-wide dashboard |
| `/planning/checkpoint` | Update feature progress |

---

## Status Values

**Ideas:** `new` → `drafting` → `promoted` | `archived`

**Drafts:** `exploring` → `ready` → `promoted` | `archived`

**Features:** `not_started` → `in_progress` → `completed` | `blocked`
