import logging
import os
from logging.handlers import TimedRotatingFileHandler

class LocalFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self,
                 filename : str,
                 when  = "h",
                 encoding  = None,
                 utc = False):
        path = os.path.join(os.getcwd(), 'instagram','logs')
        try:
            os.makedirs(path)
            print('Logs located at :' + path)
        except FileExistsError:
            print('Logs located at :' + path)
        finally:
            super(LocalFileHandler, self).__init__(filename = path+"\\"+filename,
                                                   when = when,
                                                   encoding =encoding,
                                                   utc = utc)



