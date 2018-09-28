from datetime import datetime as dt
from datetime import timedelta


def selectedTime():
    startTime = input('Start time is: ')
    endTime = input('End time is: ')
    return startTime, endTime

def defaultTime():
    format_yesterday = dt.now() - timedelta(1)
    yesterday = format_yesterday.strftime('%Y-%m-%d') + ' 00:00:00'
    format_present_day = dt.now()
    present_day = format_present_day.strftime('%Y-%m-%d') + ' 00:00:00'
    return yesterday, present_day

def formatTime():
    format_time = dt.now().strftime("%Y_%m_%d-%H-%M-%S")
    return format_time




