import logging
import os
from functools import wraps

from dotenv import load_dotenv


def get_logger():
    """
    creates logger for the project
    :return: logger object
    """

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    return logger


def get_env():
    """
    uses dotenv to get environmental variables from .env file, where to search it (relative path),
    depends on where script was started
    :return: None
    """
    basedir = os.getcwd()
    if os.path.isfile(f'{basedir}/../src/.env'):
        load_dotenv(dotenv_path=f'{basedir}/../src/.env')
    else:
        load_dotenv(dotenv_path=f'{basedir}/src/.env')


def coroutine(func):
    """
    wraps coroutine function to avoid their initialisation with none and using next
    see: https://medium.com/@chandansingh_99754/python-generators-and-coroutines-d54ed9c343ae
    see: https://praktikum.yandex.ru/learn/middle-python/courses/af061b15-1607-45f2-8d34-f88d4b21765a/sprints/5030/topics/665ba0d6-6eab-41d5-84dd-bbc1997930fb/lessons/0e75f376-4a12-422e-8fa3-64e3ef5904e5/
    :return: next
    """

    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        next(fn)
        return fn

    return inner


def id_list(series):
    """
    prepares string with ids from pandas series, is needed because {*x} does not work in f string as expected
    :param series: pandas series with ids
    :return: str with list of ids
    """
    ids = series.unique()
    ids = ', '.join("'" + str(i) + "'" for i in ids)

    return ids
