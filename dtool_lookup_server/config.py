import json
import os

import dtool_lookup_server

_HERE = os.path.abspath(os.path.dirname(__file__))

# config parameters to exclude from any config dump
CONFIG_EXCLUSIONS = [
                        "JWT_PRIVATE_KEY",
                        "SECRET_KEY",
                        "SQLALCHEMY_DATABASE_URI",
                    ]


def _get_file_content(key, default=""):
    file_path = os.environ.get(key, "")
    if os.path.isfile(file_path):
        content = open(file_path).read()
    else:
        content = ""
    return content


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY", "you-will-never-guess")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///{}".format(os.path.join(_HERE, "..", "app.db")),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ALGORITHM = "RS256"
    JWT_TOKEN_LOCATION = "headers"
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Logic to give "JWT_PUBLIC_KEY" priority over "JWT_PUBLIC_KEY_FILE".
    # This is used when making use of JWT tokens generated by another service.
    # Hence there is no need for the JWT_PRIVATE_KEY_FILE.
    if os.environ.get("JWT_PUBLIC_KEY"):
        JWT_PUBLIC_KEY = os.environ.get("JWT_PUBLIC_KEY")
    else:
        JWT_PRIVATE_KEY = _get_file_content("JWT_PRIVATE_KEY_FILE")
        JWT_PUBLIC_KEY = _get_file_content("JWT_PUBLIC_KEY_FILE")

    JSONIFY_PRETTYPRINT_REGULAR = True

    API_TITLE = "dtool-lookup-server API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = os.environ.get("OPENAPI_URL_PREFIX", "/doc")
    OPENAPI_REDOC_PATH = os.environ.get("OPENAPI_REDOC_PATH", "/redoc")
    OPENAPI_REDOC_URL = os.environ.get("OPENAPI_REDOC_URL",
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    OPENAPI_SWAGGER_UI_PATH = os.environ.get("OPENAPI_SWAGGER_UI_PATH", "/swagger")
    OPENAPI_SWAGGER_UI_URL = os.environ.get("OPENAPI_SWAGGER_UI_URL", "https://cdn.jsdelivr.net/npm/swagger-ui-dist/")

    # give API_SPEC_OPTIONS priority over API_SPEC_OPTIONS_FILE over default value
    if os.environ.get("API_SPEC_OPTIONS"):
        API_SPEC_OPTIONS = json.loads(os.environ.get("API_SPEC_OPTIONS"))
    elif os.environ.get("API_SPEC_OPTIONS_FILE"):
        API_SPEC_OPTIONS = json.loads(_get_file_content("API_SPEC_OPTIONS_FILE"))
    else:
        API_SPEC_OPTIONS = {
            "x-internal-id": "2",
            "security": [{"bearerAuth": []}],
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }

    @classmethod
    def to_dict(cls):
        """Convert server configuration into dict."""
        d = {"version": dtool_lookup_server.__version__}
        for k, v in cls.__dict__.items():
            # select only capitalized fields
            if k.upper() == k and k not in CONFIG_EXCLUSIONS:
                d[k.lower()] = v
        return d

