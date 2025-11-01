# Configuration Folder

## Purpose
- Stores templates and samples that show how the platform is configured.
- Keeps environment variables, logging settings, and rule libraries in one place.

## Contents
- `settings.env` and similar files: sample environment variable lists.
- `logging.yaml`: example logging levels and formats.
- `rules/`: versioned rule and mapping templates for tenants.
- Other JSON or YAML files used to seed the system.

## Tips for PMs and supervisors
- Treat these files as source of truth for how rules and settings are deployed.
- Any change here should go through change control and review.

