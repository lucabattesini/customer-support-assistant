import app


def test_app_package_is_importable():
    assert app.__name__ == "app"
