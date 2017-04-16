from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse
from django.db import connection
from bson import json_util
import json
import os
import requests
import httplib2
import simplejson
import eventful
import re
import time

def createHolidayEventTable(request):

    """
    @Description:
    createHolidayEventTable will create a table holiday_event to store holidays and events of every city for every date.

    """

    print("Table to be created.")
    try:
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE holiday_event \
                        (DATE varchar(255) NOT NULL, \
                        CITY varchar(255) NOT NULL, \
                        HOLIDAY text, \
                        EVENT text, \
                        CONSTRAINT PK_holiday_event PRIMARY KEY (DATE,CITY) \
                        );')

        connection.commit()

    except Exception as detail:
		print "OOPS! This is the error ==> ", detail

    return HttpResponse("Table created.")

def loadHolidays(request, city):

    """
    @Description:
    loadHolidays will call holiday API to fetch holidays for each city and store them into holiday_event table.

    """

    print("Call API for Holidays for a city")
    #JSON url to be changed for every city.
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Europe%2FAmsterdam")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2015&end_year=2016&tz=Europe%2FBrussels")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=America%2FLos_Angeles")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Europe%2FAthens")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2015&end_year=2016&tz=Europe%2FBerlin")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Europe%2FCopenhagen")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=America%2FToronto")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Europe%2FMadrid")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Europe%2FParis")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2015&end_year=2016&tz=Europe%2FRome")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Australia%2FMelbourne")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Australia%2FSydney")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Europe%2FDublin")
    # resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Europe%2FLondon")
    resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=America%2FMontreal")

    jsonResponse=json.loads(resp.text)
    cursor = connection.cursor()

    for item in jsonResponse:
        try:
            name = item.get("name")
            hddate = item.get("date")
            hdname = name+", "
            cursor.execute('INSERT INTO holiday_event \
                                (date, city, holiday, event) \
                            VALUES \
                                (%s, %s, %s, %s) \
                            ON DUPLICATE KEY UPDATE \
                                holiday = concat(holiday, %s);', (hddate, city, hdname, "  ", hdname))
            # cursor.execute('UPDATE calendar_summary SET happenings = %s WHERE city_name = %s AND date = %s', (hdname, search_string, hddate))
            connection.commit()
        except Exception as detail:
            pass


    # hddate = "2017-07-10"
    # hdname = "Suhasini's Birthday"
    #city = "Mumbai"

    # cursor = connection.cursor()
    # cursor.execute('INSERT INTO holiday_event \
    #                         (date, city, holiday) \
    #                     VALUES \
    #                         (%s, %s, %s) \
    #                     ON DUPLICATE KEY UPDATE \
    #                         holiday = concat(holiday, %s);', (hddate, city, hdname, hdname))
    #
    # connection.commit()


    return HttpResponse("Inserted holidays for "+city)

def loadEvents(requests, city):

    """
    @Description:
    loadEvents will call eventful API to fetch events for each city and date, and store them into holiday_event table.

    """

    print("Call API for Events in City "+city)

    api = eventful.API('JmGWfK7NFTc4NvX7')

    #for multiple event categories:
    # categories=['art','business','sports','health','education','theatre']
    # cities=['Brussels','Chicago','Copenhagen','Denver','Dublin','Edinburgh','Geneva','London','Hong Kong']
    #
    # for city1 in cities:
    cursor = connection.cursor()
    # for category in categories:

    events_count = 0
    try:
        # for num in range(1,4):
        events = api.call('/events/search', l=city,  t='2016050400-2017050300', page_size=250, page_number = 4, sort_order='popularity', sort_direction='descending')
        # sort_order='popularity', sort_direction='descending'
        # t='2015100300-2016061400',

        for event in events['events']['event']:
            try:
                title = event['title']
                title = title+", "
                venue_name = event['venue_name']
                start_time = event['start_time']
                start_date = start_time[0:10]
                # print start_date, title
                cursor.execute('INSERT INTO holiday_event \
                                    (date, city, event) \
                                VALUES \
                                    (%s, %s, %s) \
                                ON DUPLICATE KEY UPDATE \
                                    event = concat(event, %s);', (start_date, city, title, title))
                connection.commit()
                events_count+=1
                # time.sleep(1)
            except Exception as detail:
                print(detail)
                # return HttpResponse(events_count)
                pass
    except Exception as detail:
        print(detail)
        return HttpResponse(events_count)
        pass
                # pass



            #cursor.execute('UPDATE calendar_summary SET happenings = concat(happenings, %s) WHERE city_name = %s AND date = %s', (title, search_string, start_date))



    return HttpResponse(events_count)


def HolidayEvent(request, city, date):

    """
    @Table Structure:
    +-------+------------+-------------------------------+-------------------------------------------+
    | date  | city       |          holiday              |          event                            |
    +-------+------------+-------------------------------+-------------------------------------------+

    @Description:
    Holiday_Event will retrieve holidays and events for a city for a given date
    """

    #Access the request headers for the date
    # regex = re.compile('^HTTP_')
    # data = dict((regex.sub('', header), value) for (header, value)
    #        in request.META.items() if header.startswith('HTTP_'))
    # date = data['DATE']

    # date=1503817200
    #
    correct_date = time.strftime('%Y-%m-%d', time.localtime(1501138800))

    print correct_date

    print("doing a query on the database for city %s on date %s"%(city, date))
    # search_string = '\'%s\''%(city)

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM holiday_event WHERE city="%s" AND date = "%s"'%(city, correct_date))
    rows = cursor.fetchall()

    #Store return data from the SQL query
    result = []

    print result

    #Column values in the summary table
    keys = ('date','city_name', 'holiday', 'event')

    for row in rows:
        result.append(dict(zip(keys,row)))

    json_data = json.dumps(result, indent=4, sort_keys=True, default=str)

    return HttpResponse(json_data, content_type="application/json")
