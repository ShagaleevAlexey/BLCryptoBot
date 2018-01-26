__all__ = ['create_logger']

import logging
# from logging.handlers import RotatingFileHandler

# _FMT = '%(asctime)s: %(filename)s:%(lineno)d: [%(threadName)s]: %(name)s: %(levelname)s: %(message)s'
_FMT = '%(asctime)s: %(filename)s:%(lineno)d: %(name)s: %(levelname)s: %(message)s'

def configuration_logger(config):
    logging_config = dict(
        format=_FMT,
        level=logging.DEBUG,
        filemode='w'
    )

    logging.basicConfig(**logging_config)

configuration_logger({})


def create_logger(cfg):
    lvl = cfg.logger_config.level.upper()
    lvl = logging._nameToLevel[lvl] if lvl in logging._nameToLevel.keys() else logging.DEBUG

    log_conf = dict(
        format=_FMT,
        level=lvl,
        filemode='w' if cfg.logger_config.rewrite else 'a',
    )

    if len(cfg.logger_config.filename) > 0:
        log_conf['filename'] = cfg.logger_config.filename

    logging.basicConfig(**log_conf)

    stdout = logging.StreamHandler()
    stdout.setLevel(lvl)
    stdout.setFormatter(logging.Formatter(_FMT))
    logging.getLogger('').addHandler(stdout)


    # logger = logging.getLogger(name)
    # fmt = logging.Formatter(_FMT)
    #
    # h = RotatingFileHandler(
    #     cfg.logger_config.filename,
    #     maxBytes=cfg.logger_config.maxsize,
    #     backupCount=cfg.logger_config.backups,
    # )
    # h.setFormatter(fmt)
    # logger.addHandler(h)
    #
    # lvl = cfg.logger_config.level.upper()
    # if lvl in logging._nameToLevel.keys():
    #     lvl = logging._nameToLevel[lvl]
    # else:
    #     logging.info(f'Unknown logger level: {lvl}')
    #     lvl = logging.DEBUG
    #
    # stdh = logging.StreamHandler()
    # stdh.setFormatter(fmt)
    # logger.addHandler(stdh)
    #
    # logger.setLevel(lvl)
    # stdh.setLevel(lvl)
    #
    # return logger