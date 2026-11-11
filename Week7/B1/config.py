import os


class DefaultConfig:
    # slide 22: mọi tham số qua env, có default hợp lý cho dev — không hard-code
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-not-for-prod")
    JSON_SORT_KEYS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DB_URL", "sqlite:///products.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # flask-smorest bắt buộc các key này để tự sinh OpenAPI + Swagger UI
    API_TITLE = "Product API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


class TestConfig(DefaultConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
