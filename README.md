# modpub

A plugin-based CLI tool for syncing 3D model designs across different platforms. Currently supports Thingiverse and local directory structures.

## Features

- 🔄 **Bidirectional sync** between Thingiverse and local directories
- 🔌 **Plugin architecture** for easy extension to other platforms
- 📁 **Local directory support** with metadata preservation
- 🔐 **Flexible configuration** system with multiple sources
- 📦 **Unified model representation** for cross-platform compatibility

## Installation

### From source

```bash
git clone https://github.com/nomike/modpub.git
cd modpub
pip install -e .
```

### Development installation

```bash
pip install -e '.[dev]'
```

## Quick Start

### 1. Configure your Thingiverse token

You'll need a Thingiverse API token from https://www.thingiverse.com/apps

There are three ways to provide the token:

#### Option A: Environment variable (recommended for CI/CD)
```bash
export THINGIVERSE_TOKEN=your_token_here
```

#### Option B: Configuration file
```bash
# Create config in home directory (global)
modpub config init --location home

# Or create config in current directory (project-specific)
modpub config init --location local

# Edit the file and add your token
```

#### Option C: Direct in command (for testing)
```bash
THINGIVERSE_TOKEN=your_token modpub sync --from thingiverse:123456 --to localdir:/path
```

### 2. Sync designs

#### Download from Thingiverse
```bash
modpub sync --from thingiverse:6961850 --to localdir:./my-design
```

#### Upload to Thingiverse
```bash
# Create new thing
modpub sync --from localdir:./my-design --to thingiverse:new

# Update existing thing
modpub sync --from localdir:./my-design --to thingiverse:6961850
```

#### Copy between local directories
```bash
modpub sync --from localdir:./design-v1 --to localdir:./design-v2
```

## Configuration System

The configuration system supports multiple sources with the following precedence (highest to lowest):

1. **Environment variables** - `THINGIVERSE_TOKEN`
2. **Current directory** - `.modpub.conf`
3. **Home directory** - `~/.modpub.conf`

### Configuration file format

Configuration files use INI format:

```ini
[thingiverse]
token = your_token_here

[localdir]
# Future: default author info
author_name = Your Name
author_url = https://example.com

[defaults]
# Future: default license for new designs
license = CC-BY-4.0
```

### Configuration commands

```bash
# Show sample configuration
modpub config init

# Create config file in home directory
modpub config init --location home

# Create config file in current directory
modpub config init --location local

# Show current configuration (tokens are masked)
modpub config show
```

## Usage as Python Module

You can also run modpub as a Python module:

```bash
python -m modpub sync --from thingiverse:123456 --to localdir:./output
```

## Local Directory Structure

The `localdir` plugin uses the following structure:

```
my-design/
├── README.md           # Human-readable description and instructions
├── metadata.json       # Complete design metadata
├── files/             # STL, SCAD, 3MF, STEP files
│   ├── model.stl
│   └── source.scad
└── images/            # Photos and renders
    ├── photo1.jpg
    └── render.png
```

### metadata.json format

```json
{
  "title": "My Awesome Design",
  "description_md": "A detailed description...",
  "instructions_md": "Print with 0.2mm layers...",
  "tags": ["3d-printing", "useful"],
  "license": {
    "key": "CC-BY-4.0",
    "name": "Creative Commons - Attribution 4.0"
  },
  "author": {
    "name": "Designer Name",
    "url": "https://example.com"
  }
}
```

### README.md format

The `localdir` plugin creates human-readable README.md files with:
- Main description from design metadata
- Embedded HTML markers for round-trip preservation
- Print instructions in a dedicated section
- Automatic fallback to heading-based parsing when markers are absent

## Plugin Architecture

modpub uses a plugin-based architecture where each platform adapter implements the `RepositoryPlugin` interface:

- **Core Model** (`modpub.core.model`): Unified `Design` class for cross-platform compatibility
- **Plugin Registry** (`modpub.plugins`): Dynamic plugin loading via Python entry points
- **Plugins**: Platform-specific adapters (Thingiverse, LocalDir, etc.)

### Available Plugins

- **thingiverse**: Full read/write support for Thingiverse via their API
- **localdir**: Local directory structure with metadata preservation

### Creating Custom Plugins

Plugins are loaded via Python entry points. To create a new plugin:

1. Implement the `RepositoryPlugin` base class
2. Register in `pyproject.toml`:
   ```toml
   [project.entry-points."modpub.plugins"]
   myplugin = "mypackage.plugin:MyPlugin"
   ```

## Development

### Running tests

```bash
python -m pytest tests/
```

### Running specific tests

```bash
python -m pytest tests/test_model.py::test_roundtrip_json
```

### Project structure

```
modpub/
├── modpub/
│   ├── __init__.py
│   ├── __main__.py         # Module entry point
│   ├── cli.py             # CLI interface
│   ├── config.py          # Configuration management
│   ├── core/
│   │   ├── model.py       # Unified Design model
│   │   ├── storage.py     # File handling utilities
│   │   └── licenses.py    # License mapping
│   └── plugins/
│       ├── registry.py    # Plugin loader
│       ├── repository.py  # Base plugin interface
│       ├── thingiverse/   # Thingiverse plugin
│       └── localdir/      # Local directory plugin
└── tests/
    └── ...
```

## License Mapping

Licenses are normalized to canonical keys (e.g., `CC-BY-4.0`) and mapped to platform-specific identifiers when publishing. Unknown mappings are omitted from the outbound payload.

## Troubleshooting

### Authentication errors

If you get "THINGIVERSE_TOKEN not set" errors:
1. Check your token is correctly set: `modpub config show`
2. Verify the token at https://www.thingiverse.com/apps
3. Ensure config file has correct format (INI style)

### Plugin not found

If you get "Unknown plugin" errors after installation:
1. Reinstall in development mode: `pip install -e .`
2. Check entry points are registered: `pip show modpub`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Nomike Postmann

## Acknowledgments

- Built to solve the problem of keeping 3D designs synchronized across platforms
- Inspired by the need for better tooling in the 3D printing community
