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

def SuhaTest(request, city):

    """
    @Description:
    loadEventsAndHolidays will call APIs to fetch events and holidays from different APIs and store them into calendar_summary table.

    """
    # print("Call API for Holidays for a city")
    #
    # resp = requests.get("http://www.webcal.fi/cal.php?id=52&format=json&start_year=2016&end_year=2017&tz=%2F"+city)
    #
    # jsonResponse=json.loads(resp.text)
    # cursor = connection.cursor()
    #
    # search_string = '\'%s\''%(city)
    #
    # for item in jsonResponse:
    #     name = item.get("name")
    #     hddate = item.get("date")
    #     hdname = "$@@$"+name+"|||"
    #     cursor.execute('UPDATE calendar_summary SET happenings = %s WHERE city_name = %s AND date = %s', (hdname, search_string, hddate))
    #     connection.commit()
    #

    print("Call API for Events in a City")

    api = eventful.API('JmGWfK7NFTc4NvX7')

    events = api.call('/events/search', q='music', l=city, d='2016010100-20171231')
    cursor = connection.cursor()

    search_string = '\'%s\''%(city)

    for event in events['events']['event']:
        title = event['title']
        title = "&&##"+title+"|||"
        venue_name = event['venue_name']
        start_time = event['start_time']
        start_date = start_time[0:10]
        cursor.execute('UPDATE calendar_summary SET happenings = concat(happenings, %s) WHERE city_name = %s AND date = %s', (title, search_string, start_date))


    return HttpResponse(start_date)

def CalendarSummary(request, city):
    """
    @Table Structure:
    +------------+------------+---------------+------------------------------------------------------+
    | city_name  | date       | average_price | happenings                                           |
    +------------+------------+---------------+------------------------------------------------------+

    @Description:
    Calendar Summary will retrieve 365 days of average pricing data and events for a particular city
    """
    print("doing a query on the database for %s"%(city))
    search_string = '\'%s\''%(city)
    print(search_string)

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM calendar_summary WHERE city_name="%s"'%(search_string))
    rows = cursor.fetchall()

    #Store return data from the SQL query
    result = []

    #Column values in the summary table
    keys = ('city_name','date', 'average_price', 'happenings')

    for row in rows:
        result.append(dict(zip(keys,row)))

    json_data = json.dumps(result, indent=4, sort_keys=True, default=str)

    #Get the city information for 1 year
    return HttpResponse(json_data, content_type="application/json")
