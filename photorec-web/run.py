from config import get_config
from http_handler import create_http_app
from infrastructure import initialization


if __name__ == '__main__':
    config = get_config()
    initialization(config)

    http_app = create_http_app(config)
    http_app.run(host=config.HOST, port=config.PORT)
