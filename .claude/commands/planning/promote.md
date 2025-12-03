# Promote Draft to Epic or Feature

Promote a validated draft exploration into the formal planning hierarchy.

## Arguments

$ARGUMENTS = Draft ID (e.g., "DRAFT_advanced_caching" or just "advanced_caching")

## Instructions

1. **Load the draft** from `specs/drafts/explorations/DRAFT_<name>.md`

2. **Verify promotion readiness** by checking the Promotion Criteria section:
   - All criteria should be checked
   - If not all checked, warn user and ask to confirm

3. **Determine target placement** via interactive questions:
   ```
   Promotion Target Selection
   ══════════════════════════

   Draft: DRAFT_advanced_caching
   Summary: Advanced caching layer for contract resolution

   Where should this be placed?

   A) New Epic under existing Milestone
      → Creates: specs/milestones/<M>/epics/<new_epic>/EPIC.md
      → Then creates first feature under it

   B) New Feature under existing Epic
      → Creates: specs/milestones/<M>/epics/<E>/features/<new_feature>/

   C) Enhancement to existing Feature
      → Adds tasks to existing feature's TASKS.md

   Select [A/B/C]:
   ```

4. **For option A (New Epic):**
   - Ask which milestone (M1, M2, M3)
   - Generate epic name from draft title
   - Create EPIC.md with content from draft
   - Create first feature with IMPLEMENTATION.md and TASKS.md

5. **For option B (New Feature):**
   - Ask which milestone and epic
   - Generate feature directory name
   - Create IMPLEMENTATION.md from draft's approach
   - Create TASKS.md from draft's research notes
   - Initialize .checkpoint

6. **For option C (Enhancement):**
   - Ask which feature to enhance
   - Append new tasks to existing TASKS.md
   - Update feature's .checkpoint with new tasks

7. **Update draft status** in `.drafts_index.json` to "promoted"

8. **Update linked idea** (if any) in IDEAS.md to status "promoted"

9. **Record promotion** in draft's Session History:
   ```markdown
   | YYYY-MM-DD | Promoted | → M1/E1/feature_name |
   ```

10. **Display confirmation:**
    ```
    Draft promoted successfully!

    DRAFT_advanced_caching → specs/milestones/M1_MVP_FOUNDATION/epics/E1_CORE_VALIDATION/features/contract_caching/

    Created files:
    - IMPLEMENTATION.md (from draft approach)
    - TASKS.md (7 phases generated)
    - .checkpoint (initialized)

    Updated:
    - EPIC.md (added feature reference)
    - IDEAS.md IDEA-002 status → promoted
    - .drafts_index.json status → promoted

    Next steps:
    - `/planning/resume` to start working on the new feature
    - Review generated TASKS.md and adjust phases
    ```

## Promotion Validation

Before promoting, ensure the draft has:
- Clear problem statement
- Defined approach with technical details
- Answered key questions
- Identified target location
- Research notes that inform implementation

If validation fails:
```
Draft not ready for promotion.

Missing criteria:
- [ ] Problem clearly defined
- [ ] Target epic/feature identified

Use `/planning/draft advanced_caching` to continue exploration.
```
