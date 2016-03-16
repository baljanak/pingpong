# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser


_config = None
_config_dict = None


class ConfigError(Exception):
    pass


def get_config():
    if not _config:
        raise ConfigError("Config not setup")
    return _config


def get_config_dict():
    if not _config_dict:
        raise ConfigError("Config not setup")
    return _config_dict


def init_config(config_file, defaults=dict()):
    global _config, _config_dict
    if not _config:
        config = SafeConfigParser(defaults)
        config.optionxform = str
        config.read(config_file)
        _config_dict = {section:dict(config.items(section)) for section in config.sections()}
        _config = config
    return get_config()
