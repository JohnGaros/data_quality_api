# List Ideas and Drafts

Display all captured ideas and draft explorations with their status.

## Instructions

1. **Read IDEAS.md** and parse all `## IDEA-NNN:` entries

2. **Read `.drafts_index.json`** for draft status

3. **Display dashboard:**
   ```
   ================================================================================
   IDEAS & DRAFTS DASHBOARD
   ================================================================================

   IDEAS (specs/drafts/IDEAS.md)
   ─────────────────────────────────────────────────────────────────────────────────
   Status    ID         Summary                                          Captured
   ─────────────────────────────────────────────────────────────────────────────────
   new       IDEA-001   Real-time validation feedback via WebSockets     2025-12-03
   drafting  IDEA-002   Advanced caching layer for contracts             2025-12-02
   promoted  IDEA-003   Batch validation API endpoint                    2025-12-01
   ─────────────────────────────────────────────────────────────────────────────────
   Total: 3 ideas (1 new, 1 drafting, 1 promoted)

   DRAFTS (specs/drafts/explorations/)
   ─────────────────────────────────────────────────────────────────────────────────
   Status      Draft ID                        Origin      Last Updated
   ─────────────────────────────────────────────────────────────────────────────────
   → exploring DRAFT_advanced_caching          IDEA-002    2025-12-03
     ready     DRAFT_batch_validation          IDEA-003    2025-12-02
   ─────────────────────────────────────────────────────────────────────────────────
   Total: 2 drafts (1 exploring, 1 ready)
   Active: DRAFT_advanced_caching

   ================================================================================
   COMMANDS
   ================================================================================
   /planning/idea <description>     Capture new idea
   /planning/draft <id|name>        Create/open draft
   /planning/promote <draft>        Promote to epic/feature
   /planning/brainstorm <topic>     Start brainstorm session
   ```

4. **If no ideas or drafts exist:**
   ```
   No ideas captured yet.

   Get started:
   - `/planning/idea <description>` to capture your first idea
   - `/planning/brainstorm <topic>` to explore interactively
   ```

## Status Legend

**Ideas:**
- `new` - Just captured, not yet explored
- `drafting` - Linked to a draft exploration
- `promoted` - Promoted to epic/feature
- `archived` - Declined or superseded

**Drafts:**
- `exploring` - Active exploration
- `ready` - Ready for promotion
- `promoted` - Already promoted
- `archived` - Declined or superseded
