from modpub.core.model import Design, FileAsset, ImageAsset, Author, License, Derivative

def test_roundtrip_json():
    d = Design(
        title="Demo",
        description_md="desc",
        instructions_md="instr",
        tags=["t1"],
        license=License(key="CC-BY-4.0", name="Creative Commons Attribution 4.0"),
        author=Author(name="Nomike"),
        files=[FileAsset(filename="a.stl", path="/tmp/a.stl")],
        images=[ImageAsset(filename="p.jpg", path="/tmp/p.jpg")],
        derivatives=[Derivative(source_url="https://example.com/thing:1")],
        platform="thingiverse",
        platform_id="123",
    )
    js = d.to_json()
    d2 = Design.from_json(js)
    assert d2.title == d.title
    assert d2.license and d2.license.key == "CC-BY-4.0"
    assert d2.author and d2.author.name == "Nomike"
    assert d2.files[0].filename == "a.stl"
