from src.config import load_settings


def test_load_settings_uses_test_env_file():
    settings = load_settings(env="test")

    assert settings.app_env == "test"
    assert settings.test_database_url == "sqlite:///./ops_test.db"
    assert settings.log_level == "INFO"
