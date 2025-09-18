# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Install dependencies
```bash
pip install -e '.[dev]'
```

### Run tests
```bash
python -m pytest tests/
```

### Run a single test
```bash
python -m pytest tests/test_model.py::test_roundtrip_json
```

## Architecture Overview

modpub is a plugin-based CLI for syncing 3D model designs across different platforms. The architecture follows a clean separation of concerns:

### Core Model (`modpub.core.model`)
- `Design` class is the canonical internal representation of a 3D model/design
- Includes metadata: title, description, instructions, tags, license, author, files, images, derivatives
- Supports JSON serialization for persistence
- All plugins convert to/from this unified model

### Plugin System (`modpub.plugins`)
- Plugins are loaded via Python entry points defined in `pyproject.toml`
- Registry pattern with fallback loading mechanism
- Each plugin implements `RepositoryPlugin` base class with `read()` and `write()` methods
- Current plugins:
  - `thingiverse`: Interacts with Thingiverse API using OAuth2 Bearer tokens
  - `localdir`: Manages local directory structure with metadata.json and README.md

### LocalDir Plugin Structure
Reads/writes this directory layout:
```
my-thing/
  README.md           # Contains description and print instructions with HTML markers
  metadata.json       # Canonical Design model serialized as JSON
  files/              # Design files (STL/SCAD/3MF/STEP/etc.)
  images/             # Photos and renders
```

### CLI Usage Pattern
The main command is `modpub sync --from <source> --to <dest>` where:
- Source/destination format: `plugin:detail` (e.g., `thingiverse:123456`, `localdir:/path`)
- Special destination `thingiverse:new` creates a new Thingiverse thing
- CLI parses locators, loads plugins, reads from source, writes to destination

### Key Implementation Details
- README.md uses HTML comment markers for robust round-tripping of description/instructions
- Falls back to heuristic heading detection if markers absent
- License keys are canonicalized (e.g., `CC-BY-4.0`) and mapped to platform-specific IDs
- File operations preserve SHA256 hashes for integrity checking