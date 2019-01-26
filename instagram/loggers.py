from instagram.settings.settings import *
import logging
import os
from logging.handlers import TimedRotatingFileHandler

class LocalFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self,
                 filename : str,
                 when  = "h",
                 encoding  = None,
                 utc = False):
        path = os.path.join(cwd, 'instagram','logs')
        try:
            os.makedirs(path)
        except FileExistsError:
            print('Path already exists')
        finally:
            super(LocalFileHandler, self).__init__(filename = path+"\\"+filename,
                                                   when = when,
                                                   encoding =encoding,
                                                   utc = utc)


test = {

            "filename": "info.log",
            "when": "midnight",
            "encoding": "utf8",
			"utc" : True
        }


essai = LocalFileHandler(**test)

