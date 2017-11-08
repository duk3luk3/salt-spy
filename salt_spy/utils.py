from datetime import date
import calendar
from dateutil import relativedelta

def get_calendar():
    cal = calendar.Calendar()
    today = date.today()
    next_month = today + relativedelta.relativedelta(months=1)

    return today, cal.monthdayscalendar(today.year, today.month),cal.monthdayscalendar(next_month.year, next_month.month)
