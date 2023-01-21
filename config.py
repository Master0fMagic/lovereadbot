import os
import typing
import configparser


class Config:

    def __init__(self):
        self._logger_config = Config.LoggerConfig()
        self._bot_config = Config.BotConfig()

    class BotConfig:
        _token_env: str
        _allowed_formats: typing.List[str]
        _bot_name: str

        @property
        def token_env(self) -> str:
            return self._token_env

        @property
        def allowed_formats(self) -> typing.List[str]:
            return self._allowed_formats

        @property
        def bot_name(self) -> str:
            return self._bot_name

    class LoggerConfig:
        _level: str
        _format: str

        @property
        def level(self) -> str:
            return self._level

        @property
        def format(self) -> str:
            return self._format

    _logger_config: LoggerConfig
    _bot_config: BotConfig

    @property
    def logger_config(self) -> LoggerConfig:
        return self._logger_config

    @property
    def bot_config(self) -> BotConfig:
        return self._bot_config

    def read_config(self, config_file: str):
        cfg = configparser.ConfigParser()
        cfg.read(config_file)

        self._logger_config._format = cfg['LOGGER']['format']
        self._logger_config._level = cfg['LOGGER']['level']

        self._bot_config._allowed_formats = cfg['BOT']['allowed_formats'].split(',')
        self._bot_config._token_env = os.getenv(cfg['BOT']['token_env'])
        self._bot_config._bot_name = cfg['BOT']['name']
