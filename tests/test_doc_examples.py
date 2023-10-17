"""Test documentation examples.

This module defines a test that runs every python code block in the "docs" 
folder.

Usage:

pytest -m docs
"""

import re
from pathlib import Path
from sys import stderr

import pytest

params = [pytest.param(path, id=str(path)) for path in Path("docs").glob("**/*.md")]


@pytest.mark.docs
@pytest.mark.parametrize("path", params)
def test_doc_examples(path: Path):
    with path.open("r") as f:
        content = f.read()
        # Find all python code blocks in file
        for match in re.finditer(r"```python.*?\n([\s\S]*?)```", content):
            code = match.group(1)
            if indent := re.match(r"^(\s*)", code):
                # Remove indent from every line
                code = "\n".join([re.sub(indent.group(1), "", line, count=1) for line in code.split("\n")])
            try:
                exec(code)
            except:
                print(f"Error running code in '{path}'.", file=stderr)
                print(match.group(0), file=stderr)
                raise
