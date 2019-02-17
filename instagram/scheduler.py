import schedule as scheduler
import subprocess
from instagram import loggers, functions as fn, mongo
from instagram.settings.settings import *
import logging.config
import mongoengine
import click,random,time,copy

logging.config.dictConfig(fn.read_json_file(LOG_CONFIG))

""" Define Scheduler """

class Scheduler:

    def __init__(self):
        self.logger = logging.getLogger('Scheduler')
        self.logger.addFilter(loggers.ContextFilter())


    def get_schedules(self):
        """
        get schedules defined in database
        :return: dictionary of schedules to add to scheduler
        """
        self.logger.debug('Get schedules from database')
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
                        self.logger.error(e)
                        raise e
                result[schedule.username] = copy.deepcopy(starts)
        global schedules_to_run
        schedules_to_run = result
        self.logger.debug('Got {} schedules'.format(len(result)))
        return result


    def update(self):
        """
        delete user schedules and recreate them using the actual parameters
        """
        try:
            schedules_to_run = self.get_schedules()
        except Exception as e:
            self.logger.error(e)
            raise e
        else:
            scheduler.clear(tag='user')
            self.logger.debug('Cleared user schedules from scheduler')
            schedules = schedules_to_run
            for username in schedules:

                # randomly do not schedule the routine 15% of the time
                if random.random() > 0.85:
                    self.logger.info(f'No task scheduled for {username} today')
                else:
                    for time in schedules[username]:
                        self.logger.info(f'Set schedule for {username} at {time}')
                        args = {
                            "args" : ["C:\Scott\scott.exe", "-u", username],
                            "creationflags" : subprocess.CREATE_NEW_CONSOLE
                        }
                        scheduler.every().day.at(time).do(subprocess.Popen, **args).tag('user', 'daily')
                        self.logger.debug('Added user schedules to scheduler')


""" Run the scheduler """

@click.command()
@click.option('--debug', is_flag=True, help='Set logger level to debug')
def main(debug=False):

    # set logs level
    if debug:
        logging._handlers['console'].setLevel('DEBUG')

    sched = Scheduler()
    logger = sched.logger

    logger.info('Version: ' + SCHEDULER_VERSION)

    # configure the scheduler
    scheduler.every().day.at('00:00').do(sched.update).tag('system', 'daily')
    logger.info('Initial scheduler setting')
    scheduler.jobs[0].run()

    # add get_followers
    bot_time = '02:00'
    bot_username = 'Bot'
    args = {
        "args": ["C:\Scott\get_followers.exe", "-u", bot_username],
        "creationflags": subprocess.CREATE_NEW_CONSOLE
    }
    scheduler.every().day.at(bot_time).do(subprocess.Popen, **args).tag('system', 'daily')
    logger.info(f'Set get_followers for {bot_username} at {bot_time}')

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
