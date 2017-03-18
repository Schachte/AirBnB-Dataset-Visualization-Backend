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
    resp = requests.get("http://www.webcal.fi/cal.php?id=221&format=json&start_year=2016&end_year=2017&tz=Europe%2FBrussels")

    jsonResponse=json.loads(resp.text)
    cursor = connection.cursor()

    for item in jsonResponse:
        name = item.get("name")
        hddate = item.get("date")
        hdname = "$@@$"+name+"|||"
        cursor.execute('INSERT INTO holiday_event \
                            (date, city, holiday) \
                        VALUES \
                            (%s, %s, %s) \
                        ON DUPLICATE KEY UPDATE \
                            holiday = concat(holiday, %s);', (hddate, city, hdname, hdname))
        # cursor.execute('UPDATE calendar_summary SET happenings = %s WHERE city_name = %s AND date = %s', (hdname, search_string, hddate))
        connection.commit()

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

    print("Call API for Events in a City")

    api = eventful.API('JmGWfK7NFTc4NvX7')

    #for multiple event categories:
    categories=['music','art','business','sports','health','education','theatre']
    # cities=['Brussels','Chicago','Copenhagen','Denver','Dublin','Edinburgh','Geneva','London','Hong Kong']
    #
    # for city1 in cities:
    for category in categories:
        events = api.call('/events/search', c=category, l=city, t='2016010100-2017123100', page_size=1000, sort_order='popularity')
        cursor = connection.cursor()
        #q='music', , sort_order='popularity', sort_direction='descending'
        #business||music||art||animals||books||sports
        #search_string = '\'%s\''%(city)
        for event in events['events']['event']:
            title = event['title']
            title = "&&##"+title+"|||"
            venue_name = event['venue_name']
            start_time = event['start_time']
            start_date = start_time[0:10]
            cursor.execute('INSERT INTO holiday_event \
                                (date, city, event) \
                            VALUES \
                                (%s, %s, %s) \
                            ON DUPLICATE KEY UPDATE \
                                event = concat(event, %s);', (start_date, city, title, title))
            connection.commit()
            #cursor.execute('UPDATE calendar_summary SET happenings = concat(happenings, %s) WHERE city_name = %s AND date = %s', (title, search_string, start_date))



    return HttpResponse(title)
