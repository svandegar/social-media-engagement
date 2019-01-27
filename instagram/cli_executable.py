from instagram import routines, loggers, functions as fn
from instagram.settings.settings import *
import click
import logging
import logging.config

@click.command()
@click.option('--username', '-u', prompt=True, help='Scott username')
@click.option('--debug', is_flag=True, help='Set logger level to debug')
@click.version_option(version=VERSION)
def main(username: str, like_from_hashtags=True, debug=False):
    logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))
    routines.likes(username, like_from_hashtags, debug)

main(sys.argv[1:])
