"""CLI entrypoints for generating Data Docs (stub)."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from dq_docs.generator import DataDocsGenerator
from dq_docs.renderers.html_renderer import HtmlRenderer


def main(argv: Optional[list[str]] = None) -> None:
    """Generate Data Docs via CLI.

    TODO: wire registry/store dependencies and tenant/env flags. See
    docs/DATA_DOCS_STRATEGY.md for usage patterns.
    """

    parser = argparse.ArgumentParser(description="Generate Data Docs")
    parser.add_argument("type", choices=["contract", "job", "run"], help="Doc type to generate")
    parser.add_argument("identifier", help="ID of the contract/job/run")
    parser.add_argument("--output-dir", default="datadocs_out", help="Directory to write HTML files")
    args = parser.parse_args(argv)

    generator = DataDocsGenerator()
    renderer = HtmlRenderer()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.type == "contract":
        doc = generator.build_contract_doc(args.identifier)
        html = renderer.render_contract_doc(doc)
        (output_dir / f"contract_{args.identifier}.html").write_text(html, encoding="utf-8")
    elif args.type == "job":
        doc = generator.build_job_definition_doc(args.identifier)
        html = renderer.render_job_definition_doc(doc)
        (output_dir / f"job_{args.identifier}.html").write_text(html, encoding="utf-8")
    else:
        doc = generator.build_run_doc(args.identifier)
        html = renderer.render_run_doc(doc)
        (output_dir / f"run_{args.identifier}.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
