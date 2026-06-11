from scanomatic.image_analysis import grayscale


def test_get_grayscale_names_uses_fallback_when_user_config_missing(monkeypatch, tmp_path):
    fallback_path = tmp_path / "grayscales.cfg"
    fallback_path.write_text("[Kodak]\nsections = 23\n")

    monkeypatch.setattr(grayscale, "_GRAYSCALE_PATH", str(tmp_path / "missing.cfg"))
    monkeypatch.setattr(grayscale, "_GRAYSCALE_FALLBACK_PATH", str(fallback_path))
    monkeypatch.setattr(grayscale, "_GRAYSCALE_CONFIGS", grayscale.configparser.ConfigParser())

    assert grayscale.get_grayscale_names() == ["Kodak"]
