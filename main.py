import logging

import config
import parser as ps
import bot


def main():
    cfg = config.Config()
    cfg.read_config('config.ini')

    setup_logger(cfg.logger_config)

    parser = ps.Parser(cfg.bot_config.bot_name)

    bt = bot.LoveReadBot(cfg.bot_config, parser)
    bt.setup()
    bt.start_polling()


def setup_logger(cfg: config.Config.LoggerConfig):
    logging.basicConfig(level=cfg.level, format=cfg.format)


if __name__ == '__main__':
    main()
