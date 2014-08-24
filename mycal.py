#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test.py
#  
#  Copyright 2014 david <david@david-TECRA-A9>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

# https://docs.python.org/2/library/calendar.html
# http://pymotw.com/2/calendar/

#import svgwrite
#import pysvg

# https://docs.python.org/2/library/datetime.html

import datetime
import calendar
import csv
import pprint
pp = pprint.PrettyPrinter(indent=4)

def main():
    events = get_events()
    #pp.pprint(events)

    dates = get_dates(events)
    pp.pprint(dates)

#    for month_num, details in dates.iteritems():
#        print details

    return 0

def get_dates(events):
    now = datetime.date.today()
    c = calendar.Calendar()
    dates = {}

    year = now.year
    months = range(1, 13)
    months = range(8, 13)
    months = range(8, 9)
    for month_number in months:
        month_cal = c.itermonthdays(year, month_number)
        month = datetime.date(year, month_number, 1)
        thismonth = {'num': month_number,
                     'name': month.strftime('%B %Y'),
                     'days': {}}

        for day_number in month_cal:
            if day_number:
                day = datetime.date(year, month_number, day_number)
                thismonth['days'][day_number] = {'label': day.strftime('%d %a')[:-2]}
                if (month_number in events):
                    #print events[month_number]
                    if (day_number in events[month_number]):
                        thismonth['days'][day_number]['events'] = events[month_number][day_number]

        dates[month_number] = (thismonth)

    return dates

def get_events():
    fp = file('events.csv')
    rdr = csv.DictReader(filter(lambda row: row[0]!='#', fp))
    events = {}
    for row in rdr:
        date_split = row['date'].split('-')
        del row['date']
        date = {'month': int(date_split[1]),
                'day': int(date_split[2])}
        try:
            date['year'] = int(date_split[0])
        except:
            pass
        row['date'] = date

        if not(date['month'] in events):
            events[date['month']] = {}

        if not(date['day'] in events[date['month']]):
            events[date['month']][date['day']] = []

        events[date['month']][date['day']].append(row)

    return events

if __name__ == '__main__':
    main()

