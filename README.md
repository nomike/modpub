# modpub — 3D Model Publisher

An extensible, plugin-based CLI to **fetch**, **export**, **publish**, and **update** 3D model designs across platforms like Thingiverse and your local directory layout.

## Highlights
- Canonical internal model (`Design`) for metadata, files, images, tags, license, authors, derivatives.
- Pluggable architecture via Python entry points (`modpub.plugins`).
- Providers in this release:
  - `thingiverse`: read/publish/update via the Thingiverse API (OAuth2 Bearer tokens).
  - `localdir`: round-trip between the internal model and a local directory you can commit to Git.
- Non-interactive CLI now; a GUI can be added later on top of the core library.

## Install
```bash
pip install .
# dev
pip install -e '.[dev]'
```

## Configure
Set the Thingiverse access token:
```bash
export THINGIVERSE_TOKEN=your_access_token
```

## CLI usage
```bash
# Download a Thingiverse thing into a local directory
modpub sync --from thingiverse:123456 --to localdir:/path/to/my-thing

# Make edits locally (README.md, files/, images/), then update the existing Thingiverse thing
modpub sync --from localdir:/path/to/my-thing --to thingiverse:123456

# Create a NEW Thingiverse thing from a local directory
modpub sync --from localdir:/path/to/my-thing --to thingiverse:new
```

### README.md in local directories
- `localdir` writes a single `README.md` with both general description and a `## Print Instructions` section.
- Embedded HTML markers ensure robust round-tripping.
- When reading, if markers are absent, it splits on headings like `## Print Instructions` / `## Print Settings`.
- If no split is possible, the whole README becomes the description and instructions remain empty.

### License mapping
- Licenses are normalized to canonical keys (e.g., `CC-BY-4.0`) and mapped to provider-specific identifiers when publishing. If a mapping is unknown, the license is omitted from the outbound payload.

## Directory schema (localdir)
```
my-thing/
  README.md           # human docs (description + print instructions)
  metadata.json       # canonical internal model
  files/              # design files (STL/SCAD/3MF/STEP/ZIP/...)
  images/             # photos/renders
```
