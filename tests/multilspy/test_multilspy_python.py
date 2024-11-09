"""
This file contains tests for running the Python Language Server: jedi-language-server
"""

import pytest
from multilspy import LanguageServer
from multilspy.multilspy_config import Language
from tests.test_utils import create_test_context
from pathlib import PurePath

pytest_plugins = ("pytest_asyncio",)

@pytest.mark.asyncio
async def test_multilspy_python_black():
    """
    Test the working of multilspy with python repository - black
    """
    code_language = Language.PYTHON
    params = {
        "code_language": code_language,
        "repo_url": "https://github.com/psf/black/",
        "repo_commit": "f3b50e466969f9142393ec32a4b2a383ffbe5f23"
    }
    with create_test_context(params) as context:
        lsp = LanguageServer.create(context.config, context.logger, context.source_directory)

        # All the communication with the language server must be performed inside the context manager
        # The server process is started when the context manager is entered and is terminated when the context manager is exited.
        # The context manager is an asynchronous context manager, so it must be used with async with.
        async with lsp.start_server():
            result = await lsp.request_definition(str(PurePath("src/black/mode.py")), 163, 4)

            assert isinstance(result, list)
            assert len(result) == 1
            item = result[0]
            assert item["relativePath"] == str(PurePath("src/black/mode.py"))
            assert item["range"] == {
                "start": {"line": 163, "character": 4},
                "end": {"line": 163, "character": 20},
            }

            result = await lsp.request_references(str(PurePath("src/black/mode.py")), 163, 4)

            assert isinstance(result, list)
            assert len(result) == 8

            for item in result:
                del item["uri"]
                del item["absolutePath"]

            assert result == [
                {
                    "relativePath": str(PurePath("src/black/__init__.py")),
                    "range": {
                        "start": {"line": 71, "character": 4},
                        "end": {"line": 71, "character": 20},
                    },
                },
                {
                    "relativePath": str(PurePath("src/black/__init__.py")),
                    "range": {
                        "start": {"line": 1105, "character": 11},
                        "end": {"line": 1105, "character": 27},
                    },
                },
                {
                    "relativePath": str(PurePath("src/black/__init__.py")),
                    "range": {
                        "start": {"line": 1113, "character": 11},
                        "end": {"line": 1113, "character": 27},
                    },
                },
                {
                    "relativePath": str(PurePath("src/black/mode.py")),
                    "range": {
                        "start": {"line": 163, "character": 4},
                        "end": {"line": 163, "character": 20},
                    },
                },
                {
                    "relativePath": str(PurePath("src/black/parsing.py")),
                    "range": {
                        "start": {"line": 7, "character": 68},
                        "end": {"line": 7, "character": 84},
                    },
                },
                {
                    "relativePath": str(PurePath("src/black/parsing.py")),
                    "range": {
                        "start": {"line": 37, "character": 11},
                        "end": {"line": 37, "character": 27},
                    },
                },
                {
                    "relativePath": str(PurePath("src/black/parsing.py")),
                    "range": {
                        "start": {"line": 39, "character": 14},
                        "end": {"line": 39, "character": 30},
                    },
                },
                {
                    "relativePath": str(PurePath("src/black/parsing.py")),
                    "range": {
                        "start": {"line": 44, "character": 11},
                        "end": {"line": 44, "character": 27},
                    },
                },
            ]
            
            # Test document symbols functionality
            symbols, tree = await lsp.request_document_symbols(str(PurePath("src/black/mode.py")))
            
            # Verify flat list of symbols
            assert isinstance(symbols, list)
            assert len(symbols) > 0
            
            # Check a few known symbols that should be in the file
            symbol_names = {s["name"] for s in symbols}
            assert "TargetVersion" in symbol_names
            assert "Feature" in symbol_names
            
            # Verify tree representation
            assert isinstance(tree, list)
            assert len(tree) > 0
            
            # The tree should contain at least one class-level entry (TargetVersion or Feature)
            class_entry = next((t for t in tree if 5 in t), None)  # 5 is SymbolKind.Class
            assert class_entry is not None
            
            # The class should have child nodes (methods, fields, etc.)
            assert isinstance(class_entry[5], list)
            assert len(class_entry[5]) > 0