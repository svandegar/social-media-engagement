import schedule as scheduler
from instagram import routines, loggers, functions as fn, mongo
from instagram.settings.settings import *
import logging.config
import mongoengine
import copy
import time
import click

logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))
logger = logging.getLogger(__name__)

""" Define functions """

def get_schedules():
    """
    get schedules defined in database
    :return: dictionary of schedules to add to scheduler
    """
    logger.debug('Get schedules from database')
    mongoengine.connect(host=fn.read_json_file(CONFIG_FILE)['databases']['Mongo'])
    schedules = mongo.Schedules.objects()
    result = {}
    for schedule in schedules:
        if schedule.schedule_activated:
            starts = []
            for times in schedule.schedules:
                start = fn.random_time(times[0], times[1])
                starts.append(start)
            result[schedule.username] = copy.deepcopy(starts)
    global schedules_to_run
    schedules_to_run = result
    logger.debug('Got {} schedules'.format(len(result)))
    return result


def update_scheduler():
    """
    delete user schedules and recreate them using the actual parameters
    """
    try :
        schedules_to_run = get_schedules()
    except Exception as e :
        logger.error(e)
        raise e
    else :
        scheduler.clear(tag='user')
        logger.debug('Cleared user schedules from scheduler')
        schedules = schedules_to_run
        for username in schedules:
            for time in schedules[username]:
                logger.info('Set schedule for {} at {}'.format(username, time))
                scheduler.every().day.at(time).do(routines.likes, username=username).tag('user', 'daily')
        logger.debug('Added user schedules to scheduler')

""" Schedule the scheduler updater """

@click.command()
@click.option('--debug', is_flag=True, help='Set logger level to debug')
def main(debug = False):
    #configure the logs level
    if debug:
        logging._handlers['console'].setLevel('DEBUG')

    #configure the scheduler
    scheduler.every().day.at('00:00').do(update_scheduler).tag('system', 'daily')
    logger.info('Initial scheduler setting')
    scheduler.jobs[0].run()

    # run the scheduler
    logger.info('Scheduler launched')
    click.echo('Scheduler running ...')
    while True:
        try:
            scheduler.run_pending()
            time.sleep(1)

        except Exception as e:
            logger.error(e)
            break

main(sys.argv[1:])
