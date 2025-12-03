# Create or Open Draft Exploration

Create a new draft document for exploring an idea, or open an existing one.

## Arguments

$ARGUMENTS = Either an IDEA-NNN reference or a descriptive name (e.g., "advanced_caching")

## Instructions

1. **Parse the argument:**
   - If starts with "IDEA-": Link to existing idea in IDEAS.md
   - Otherwise: Create standalone draft with given name

2. **Check if draft exists** in `.drafts_index.json`:
   - If exists: Open and display the existing draft
   - If not: Create new draft

3. **For new draft, create** `specs/drafts/explorations/DRAFT_<name>.md`:
   ```markdown
   # Draft: <Title>

   **Created:** YYYY-MM-DD
   **Status:** exploring
   **Origin:** IDEA-NNN (if applicable) | standalone
   **Target:** <!-- epic/feature when known -->

   ## Problem Statement

   <!-- What problem does this solve? -->

   ## Proposed Approach

   <!-- High-level solution outline -->

   ## Key Questions

   - [ ] <!-- Question 1 -->
   - [ ] <!-- Question 2 -->

   ## Research Notes

   <!-- Findings from codebase exploration -->

   ## Technical Considerations

   <!-- Architecture implications, dependencies, risks -->

   ## Promotion Criteria

   - [ ] Problem clearly defined
   - [ ] Approach validated
   - [ ] Key questions answered
   - [ ] Target epic/feature identified
   - [ ] Effort estimated

   ## Session History

   | Date | Activity | Outcome |
   |------|----------|---------|
   | YYYY-MM-DD | Created | Initial exploration |

   ---
   ```

4. **Update `.drafts_index.json`:**
   ```json
   {
     "drafts": [
       {
         "id": "DRAFT_<name>",
         "title": "<Title>",
         "origin_idea": "IDEA-NNN" | null,
         "status": "exploring",
         "created": "YYYY-MM-DD",
         "last_updated": "YYYY-MM-DD",
         "file": "explorations/DRAFT_<name>.md"
       }
     ],
     "active_draft": "DRAFT_<name>"
   }
   ```

5. **If linked to IDEA-NNN**, update IDEAS.md entry status to "drafting"

6. **Display to user:**
   ```
   Draft created/opened: DRAFT_<name>
   Location: specs/drafts/explorations/DRAFT_<name>.md

   Current status: exploring
   Origin: IDEA-NNN | standalone

   Next steps:
   - Fill in problem statement and approach
   - Use `/planning/brainstorm <topic>` for focused exploration
   - Use `/planning/promote <name>` when ready to formalize
   ```

## Example

User: `/planning/draft IDEA-001`

Creates `specs/drafts/explorations/DRAFT_realtime_validation_websockets.md` linked to IDEA-001.
