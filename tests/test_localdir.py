from pathlib import Path
from modpub.plugins.localdir.plugin import LocalDirPlugin
from modpub.core.model import Design, FileAsset, ImageAsset

def test_localdir_roundtrip(tmp_path: Path):
    plugin = LocalDirPlugin()
    src_file = tmp_path / "src.stl"
    src_file.write_bytes(b"123")
    src_img = tmp_path / "img.jpg"
    src_img.write_bytes(b"456")

    d = Design(title="Demo", files=[FileAsset(filename="src.stl", path=str(src_file))], images=[ImageAsset(filename="img.jpg", path=str(src_img))])

    out_dir = tmp_path / "out"
    loc = plugin.write(d, str(out_dir), mode="create")
    assert Path(loc).exists()

    d2 = plugin.read(str(out_dir))
    assert d2.title == "Demo"
    assert d2.files[0].filename == "src.stl"
