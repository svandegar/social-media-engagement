import schedule as scheduler
from instagram import routines, loggers, functions as fn, mongo
from instagram.settings.settings import *
import logging.config
import mongoengine
import threading
import copy
import time
import click


logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))
logger = logging.getLogger('Scheduler')
logger.addFilter(loggers.ContextFilter())

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
                try:
                    start = fn.random_time(times[0], times[1])
                    starts.append(start)
                except ValueError as e:
                    logger.error(e)
                    raise e
            result[schedule.username] = copy.deepcopy(starts)
    global schedules_to_run
    schedules_to_run = result
    logger.debug('Got {} schedules'.format(len(result)))
    return result


def update_scheduler():
    """
    delete user schedules and recreate them using the actual parameters
    """
    try:
        schedules_to_run = get_schedules()
    except Exception as e:
        logger.error(e)
        raise e
    else:
        scheduler.clear(tag='user')
        logger.debug('Cleared user schedules from scheduler')
        schedules = schedules_to_run
        for username in schedules:
            for time in schedules[username]:
                logger.info('Set schedule for {} at {}'.format(username, time))
                scheduler.every().day.at(time).do(run_threaded, routines.likes, username).tag('user', 'daily')
        logger.debug('Added user schedules to scheduler')


def run_threaded(job_func, *args):
    """
    run the function in a new thread
    :param job_func: function to run
    :args: args to pass to the function
    :return:
    """
    job_thread = threading.Thread(target=job_func, args=args)
    job_thread.start()


""" Run the scheduler """


@click.command()
@click.option('--debug', is_flag=True, help='Set logger level to debug')
def main(debug=False):
    logger.info('Version: ' + VERSION)
    # configure the logs level
    if debug:
        logging._handlers['console'].setLevel('DEBUG')

    # configure the scheduler
    scheduler.every().day.at('00:00').do(run_threaded, update_scheduler).tag('system', 'daily')
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
