'''
Created on Feb 27, 2017
Updated for Python 3 compatibility

@author: joigno
'''

from datetime import datetime

class DateRange(object):
    '''
    classdocs
    '''

    # Set to current date
    current_date = datetime.now()
    endMonth = current_date.month
    endDay = current_date.day
    endYear = current_date.year

    def __init__(self, params=None):
        '''
        Constructor
        '''
        pass
