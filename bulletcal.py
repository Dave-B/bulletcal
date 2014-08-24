#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bulletcal.py
#
#  Copyright 2014 David Balch <david@balch.co.uk>
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

import datetime
import calendar
import csv
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)

import xml.etree.ElementTree as ET
ET.register_namespace('svg', 'http://www.w3.org/2000/svg')

template = 'resources/template.svg'
abbr = {'Birthday': 'B', 'Married': 'A'}
now = datetime.date.today()

def main():
    events = get_events()
    #pp.pprint(events)

    dates = get_dates(events)
    #pp.pprint(dates)

    #date_list(dates)
    date_plot(dates)

    return 0


def date_plot(dates):
    # Write out calendar as SVG files.
    for page_num in range(1, 13, 2):
        # Two months per page.
        page_name = "out/page_%d-%d.svg" % (page_num, page_num + 1)
        page = ET.parse(template)
        root = page.getroot()

        root.append(svg_month(dates[page_num]))
        root.append(svg_month(dates[page_num + 1], True))

        page.write(page_name)


def svg_month(month_details, second_page = False):
    # Build month in SVG
    offset_v = 10
    offset_h = 10
    if second_page:
        offset_h = 150
    text_offset_v = 9

    the_id = month_details['name'].split(' ')[0]
    text_size = '5'
    text_font = 'Courier'

    g = ET.Element('svg:g', {
                             'transform': "translate(%d,%d)" % (offset_h, offset_v),
                             'id': the_id})

    rect = ET.Element('svg:rect', {'width': '135',
                                   'height': '190',
                                   'fill': 'url(#grid)'})
    g.append(rect)

    header = ET.Element('svg:text', {'x': '5',
                                     'y': str(text_offset_v),
                                      'font-size': text_size,
                                     'font-family': text_font})
    header.text = month_details['name']
    g.append(header)

    text_offset_v = text_offset_v + 5
    for day_num, day_details in month_details['days'].iteritems():
        text_offset_v = text_offset_v + 5
        day = ET.Element('svg:text', {'x': '5',
                                      'y': str(text_offset_v),
                                      'font-size': text_size,
                                      'font-family': text_font})
        o = day_details['label'] + ' '
        if 'events' in day_details:
            event_list = []
            for event in day_details['events']:
                event_txt = abbr[event['event']]
                if ('year' in event['date']):
                    age = now.year - event['date']['year']
                    event_txt = event_txt + str(age)
                event_txt = event_txt + event['nickname']
                event_list.append(event_txt)
            o = o + ','.join(event_list)
        day.text = o

        g.append(day)

    return g


def date_list(dates):
    # Print out calendar in text.
    for month_num, month_details in dates.iteritems():
        print month_details['name']
        for day_num, day_details in month_details['days'].iteritems():
            o = day_details['label'] + ': '
            if 'events' in day_details:
                for event in day_details['events']:
                    #print event
                    o = o + event['event'] + ': ' + event['nickname']
            print o
        print ''


def get_dates(events):
    # Generate list of calendar dates, incorporating events.
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

