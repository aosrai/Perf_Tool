from datetime import datetime as dt
from datetime import timedelta

def SelectedTime():
    start_time = input('Start time is: ')
    end_time = input('End time is: ')
    return start_time, end_time

def DefaultTime():
    format_yesterday = dt.now() - timedelta(1)
    yesterday = format_yesterday.strftime('%Y-%m-%d') + ' 08:00:00'
    format_present_day = dt.now()
    present_day = format_present_day.strftime('%Y-%m-%d') + ' 08:00:00'
    return yesterday, present_day




