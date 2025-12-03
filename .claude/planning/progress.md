Display project-wide progress dashboard using checkpoint data.

**Your task:**

1. Run `python scripts/parse_checkpoints.py` from the project root

2. Parse the JSON output from the script

3. Display a formatted dashboard in this format:

```
## Project Progress Dashboard

Generated: [current timestamp]

### Overall Summary

Total Features: [total_features]
Completed: [completed] ([X]%)
In Progress: [in_progress] ([X]%)
Not Started: [not_started] ([X]%)
Blocked: [blocked] ([X]%)

### By Milestone

#### M1: MVP Foundation - [X]%
[List epics with their completion %]
  - E1: Core Validation - [X]% ([completed]/[total] features)
  - E2: Metadata & Lineage - [X]% ([completed]/[total] features)

#### M2: Security & Compliance - [X]%
[Same format]

#### M3: Scale & Operations - [X]%
[Same format]

### Active Features

[List all in_progress features with current phase and progress]

### Blocked Features

[List all blocked features with blocker details]

### Recently Completed

[List 5 most recently completed features with completion timestamps]

### Next Steps

- Resume work: /planning/resume
- Start new feature: /planning/goto-feature [name]
- Update progress: /planning/checkpoint
```

**Alternative Output Format (if script returns detailed data):**

Show a tree view:
```
specs/
├── M1_MVP_FOUNDATION (67% complete)
│   ├── E1_CORE_VALIDATION (75% complete)
│   │   ├── core_rule_engine (in_progress - 42%)
│   │   ├── api_upload_endpoints (not_started - 0%)
│   │   └── e2e_file_testing (not_started - 0%)
│   └── E2_METADATA_LINEAGE (25% complete)
│       └── audit_trail (in_progress - 25%)
├── M2_SECURITY_COMPLIANCE (0% complete)
└── M3_SCALE_OPERATIONS (0% complete)
```

**Performance:**
- Should execute in < 5 seconds
- Caches parse_checkpoints.py output if run multiple times in same session
