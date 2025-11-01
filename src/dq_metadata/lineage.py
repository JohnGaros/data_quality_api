"""Utilities for constructing lineage graphs from metadata entities."""

from collections import defaultdict
from typing import Dict, List
from uuid import UUID

from .models import RuleVersionMetadata, ValidationJobMetadata


def build_job_lineage(
    jobs: List[ValidationJobMetadata],
    rule_versions: List[RuleVersionMetadata],
) -> Dict[str, Dict[str, List[str]]]:
    """Create a simple lineage map linking jobs to rule versions and assets.

    Returns:
        Dictionary keyed by job_id containing referenced assets and rule versions.
    """
    lineage_map: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: {"assets": [], "rule_versions": []})

    for job in jobs:
        lineage_map[job.job_id]["assets"] = [str(asset_id) for asset_id in job.input_assets]

    for version in rule_versions:
        lineage_map[version.rule_id]["rule_versions"].append(str(version.rule_version_id))

    return lineage_map


def relate_asset_to_job(asset_id: UUID, job: ValidationJobMetadata) -> bool:
    """Determine whether a data asset participated in a given job run."""
    return asset_id in job.input_assets
