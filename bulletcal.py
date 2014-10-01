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
import os

import xml.etree.ElementTree as ET
ET.register_namespace('svg', 'http://www.w3.org/2000/svg')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--events", default="events.csv", help="CSV file of repeating events to include in calendars (default: events.csv).")
parser.add_argument("-o", "--outputdir", default="out", help="Directory to save calendar files (default: out).")
parser.add_argument("-y", "--year", help="Year to generate calendars for (default: the current year).")
args = parser.parse_args()

template = 'resources/template.svg'
abbr = {'Birthday': 'B', 'Married': 'A'}
if (args.year):
    year = int(args.year)
else:
    now = datetime.date.today()
    year = now.year


def main():
    if (os.path.isfile(args.events)):
        events = get_events()
    else:
        events = {}

    dates = get_dates(events)
    date_plot(dates)

    return 0


def date_plot(dates):
    # Ensure we have an output dir.
    if not os.path.exists(args.outputdir):
        os.makedirs(args.outputdir)

    # Write out calendar as SVG files.
    for page_num in range(1, 13, 2):
        # Two months per page.
        page_name = "%s/page_%d-%d.svg" % (args.outputdir, page_num, page_num + 1)
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
    text_offset_v = 9.5

    the_id = month_details['name'].split(' ')[0]
    text_size = '4'
    text_font = 'Arial'

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
        day.text = day_details['label']
        g.append(day)

        if 'events' in day_details:
            event_list = []
            for event in day_details['events']:
                event_txt = abbr[event['event']]
                if ('year' in event['date']):
                    age = year - event['date']['year']
                    event_txt = event_txt + str(age)
                event_txt = event_txt + event['nickname']
                event_list.append(event_txt)

            events = ET.Element('svg:text', {'x': '15.5',
                                          'y': str(text_offset_v),
                                          'font-size': text_size,
                                          'font-family': text_font})
            events.text = ','.join(event_list)
            g.append(events)

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
    fp = file(args.events)
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

