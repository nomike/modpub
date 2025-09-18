from pathlib import Path
from modpub.plugins.localdir.plugin import LocalDirPlugin
from modpub.core.model import Design

def test_readme_roundtrip_with_markers(tmp_path: Path):
    plugin = LocalDirPlugin()
    d = Design(title="Widget", description_md="General desc", instructions_md="Print at 0.2mm")
    out_dir = tmp_path / "widget"
    plugin.write(d, str(out_dir), mode="create")

    readme = (out_dir / "README.md").read_text(encoding="utf-8")
    assert "modpub:begin:description" in readme
    assert "modpub:begin:instructions" in readme

    d2 = plugin.read(str(out_dir))
    assert d2.description_md.strip() == "General desc"
    assert d2.instructions_md.strip() == "Print at 0.2mm"


def test_readme_heuristic_split(tmp_path: Path):
    plugin = LocalDirPlugin()
    out_dir = tmp_path / "heuristic"
    out_dir.mkdir(parents=True, exist_ok=True)
    # minimal metadata.json
    (out_dir / "metadata.json").write_text(Design(title="H").to_json(), encoding="utf-8")
    (out_dir / "files").mkdir(exist_ok=True)
    (out_dir / "images").mkdir(exist_ok=True)
    # README without markers
    (out_dir / "README.md").write_text(
        """# H

This is general.

## Print Instructions
Use 0.28mm layer height.
""",
        encoding="utf-8"
    )
    d2 = plugin.read(str(out_dir))
    assert "general" in d2.description_md.lower()
    assert "0.28mm" in d2.instructions_md
