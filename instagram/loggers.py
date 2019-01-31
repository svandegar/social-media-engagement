import logging
import os
from logging.handlers import TimedRotatingFileHandler, SysLogHandler
import socket


class LocalFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self,
                 filename : str,
                 when  = "h",
                 encoding  = None,
                 utc = False):
        path = os.path.join(os.getcwd(), 'instagram','logs')
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        finally:
            super(LocalFileHandler, self).__init__(filename = path+"\\"+filename,
                                                   when = when,
                                                   encoding =encoding,
                                                   utc = utc)

class ContextFilter(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = ContextFilter.hostname
        return True