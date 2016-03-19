import datetime as dt

def get_dates_from_week(year,week):

     d = dt.date(year,1,1)
     if(d.weekday()<= 3):
         d = d - dt.timedelta(d.weekday()+1)             
     else:
         d = d + dt.timedelta(7-(d.weekday()+1))
     dlt = dt.timedelta(days = (week-1)*7)
     return d + dlt,  d + dlt + dt.timedelta(days=6)

def FloorDatetime(datetime,time_slice_amt):

    if not(time_slice_amt == 60):
        datetime = datetime - dt.timedelta(
                                            minutes=datetime.minute % time_slice_amt,
                                            seconds=datetime.second,
                                            microseconds=datetime.microsecond)
    return datetime
    
def CeilingDatetime(datetime,time_slice_amt):
    
    if time_slice_amt == 60:
        return datetime
    elif datetime.minute % time_slice_amt == 0:
        return datetime
    else:
        datetime = FloorDatetime(datetime,time_slice_amt)
        if (datetime.minute + time_slice_amt) == 60:

            if datetime.hour == 23:
                datetime = datetime.replace(hour = 0)
            else:
                datetime = datetime.replace(hour = datetime.hour +1)

            datetime = datetime.replace(minute=0)
        else:
            datetime = datetime.replace(minute = datetime.minute + time_slice_amt)
        return datetime