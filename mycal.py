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
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)

import xml.etree.ElementTree as ET
ET.register_namespace('svg', 'http://www.w3.org/2000/svg')

bell = 'E004'
candle = 'E006'

def main():
    events = get_events()
    #pp.pprint(events)

    dates = get_dates(events)
    #pp.pprint(dates)

    #date_list(dates)
    tree = ET.parse('resources/template.svg')
    date_plot(dates, tree)

    return 0


def date_plot(dates, svg):
    # Write out calendar as SVG files.

    # Two months per page.
    for page_num in range(1, 13, 2):
        page_name = "out/page_%d-%d.svg" % (page_num, page_num + 1)
        page = copy.copy(svg)
        root = page.getroot()

        root.append(svg_month(dates[page_num]))
        #root.append(svg_month(dates[page_num + 1]))

        page.write(page_name)
        del page


def svg_month(month_details):
    # Build month in SVG
    text_offset = 5
    text_size = '5mm'
    text_font = 'Courier'
    g = ET.Element('svg:g', {'x': '5mm',
                             'y': str(text_offset)+ 'mm'})


    rect = ET.Element('svg:rect', {'width': '136mm',
                                   'height': '196mm',
                                   'fill': 'url(#grid)'})
    g.append(rect)

    header = ET.Element('svg:text', {'x': '5mm',
                                     'y': str(text_offset)+ 'mm',
                                     #'height': text_size,
                                     'font-family': text_font})
    header.text = month_details['name']
    g.append(header)

    for day_num, day_details in month_details['days'].iteritems():
        text_offset = text_offset +5
        #print day_details
        day = ET.Element('svg:text', {'x': '5mm',
                                      'y': str(text_offset) + 'mm',
                                      #'height': text_size,
                                      'font-family': text_font})
        o = day_details['label'] + ': '
        if 'events' in day_details:
            for event in day_details['events']:
                #print event
                    o = o + event['event'] + ': ' + event['nickname']
        day.text = o

        g.append(day)

    return g


def date_list(dates):
    # Print out calendar in text.
    for month_num, month_details in dates.iteritems():
        print month_details['name']
        for day_num, day_details in month_details['days'].iteritems():
            #print day_details
            o = day_details['label'] + ': '
            if 'events' in day_details:
                for event in day_details['events']:
                    #print event
                    o = o + event['event'] + ': ' + event['nickname']
            print o
        print ''


def get_dates(events):
    # Generate list of calendar dates, incorporating events.
    now = datetime.date.today()
    c = calendar.Calendar()
    dates = {}

    year = now.year
    months = range(1, 13)
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
    # Load CSV of events.
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

