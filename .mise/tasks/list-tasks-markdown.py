# -*- coding: utf-8 -*-

"""
Generate a Markdown document listing all available mise tasks.
This is useful for AI to understand what commands are available.
"""

import json
import subprocess
from pathlib import Path


def main():
    # Get tasks in JSON format
    result = subprocess.run(
        ["mise", "tasks", "ls", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    tasks = json.loads(result.stdout)

    # Group tasks by category (inferred from comments in mise.toml)
    categories = {
        "Environment Management": [],
        "Dependency Management": [],
        "Testing": [],
        "Documentation": [],
        "Building & Publishing": [],
        "GitHub Release Management": [],
        "CI/CD Setup": [],
        "Documentation Tools": [],
    }

    # Simple categorization based on task names
    for task in tasks:
        name = task["name"]
        if name.startswith("venv"):
            categories["Environment Management"].append(task)
        elif name in ["inst", "export"]:
            categories["Dependency Management"].append(task)
        elif name in ["test", "cov", "view-cov"]:
            categories["Testing"].append(task)
        elif name in ["build-doc", "view-doc"]:
            categories["Documentation"].append(task)
        elif name in ["build", "publish"]:
            categories["Building & Publishing"].append(task)
        elif name == "release":
            categories["GitHub Release Management"].append(task)
        elif name.startswith("setup-") or name == "update-github-metadata":
            categories["CI/CD Setup"].append(task)
        elif name == "notebook-to-markdown":
            categories["Documentation Tools"].append(task)

    # Generate Markdown
    output = ["# Available Mise Tasks", ""]
    output.append("This document lists all available mise tasks for this project.")
    output.append("")
    output.append("## Quick Reference")
    output.append("")
    output.append("| Command | Description |")
    output.append("|---------|-------------|")

    for task in sorted(tasks, key=lambda x: x["name"]):
        output.append(f"| `mise run {task['name']}` | {task['description']} |")

    output.append("")
    output.append("## Tasks by Category")
    output.append("")

    for category, task_list in categories.items():
        if not task_list:
            continue

        output.append(f"### {category}")
        output.append("")

        for task in task_list:
            output.append(f"**`mise run {task['name']}`**")
            output.append(f"- {task['description']}")

            if task["depends"]:
                deps = ", ".join(f"`{d}`" for d in task["depends"])
                output.append(f"- Dependencies: {deps}")

            if task["run"]:
                run_cmd = " ".join(task["run"]) if isinstance(task["run"], list) else task["run"]
                if len(run_cmd) < 100:
                    output.append(f"- Command: `{run_cmd}`")

            output.append("")

    # Write to file
    output_file = Path(".claude/mise-tasks.md")
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text("\n".join(output))

    print(f"✅ Generated: {output_file}")
    print(f"   Total tasks: {len(tasks)}")


if __name__ == "__main__":
    main()
