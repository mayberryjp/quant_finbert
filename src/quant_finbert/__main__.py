from waitress import serve

from quant_finbert.api.app import create_app
from quant_finbert.config import settings
from quant_finbert.logging import configure_logging


def main() -> None:
    configure_logging(settings.log_level)
    app = create_app()
    serve(app, host=settings.api_listen_address, port=settings.api_port)


if __name__ == "__main__":
    main()
