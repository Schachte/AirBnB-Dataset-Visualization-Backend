from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
from bson import json_util
import unicodedata
import json, ast
import os
import requests
import httplib2
import simplejson
import eventful
from django.views.decorators.csrf import csrf_exempt

def Uptime(request):
    return HttpResponse("Up!")


def CityReviews(request, city):
    """
    @Description:
    Calendar Summary will retrieve 365 days of average pricing data and events for a particular city
    """
    print("doing a query on the database for %s"%(city))

    #Column values in the summary table
    keys = ('city_name', 'comments')
    cursor = connection.cursor()
    if(city.lower() == 'all'):
        # cursor.execute('SELECT city_name, comments FROM reviews')
        city_arr = ['Amsterdam','Antwerp','Asheville','Athens','Austin','Barcelona','Berlin','Boston','Brussels','Chicago','Copenhagen','Denver','Dublin','Edinburgh','Geneva','Hong Kong','London','Los Angeles','Madrid','Mallorca','Manchester','Melbourne','Montreal','Nashville', 'New Orleans','New York City','Northern Rivers','Oakland','Paris','Portland','Quebec City','San Diego','San Francisco','Santa Cruz County','Seattle','Sydney','Toronto','Trentino','Vancouver','Venice','Victoria','Vienna','Washington DC']
        result = []
        for city in city_arr:
            cursor.execute('SELECT city_name, comments FROM reviews WHERE city_name like "%s" limit 500'%(city))
            rows = cursor.fetchall()
            for row in rows:
                row = list(row)
                row[1] = unicodedata.normalize('NFKD', row[1]).encode('ascii','ignore')
                row[1] = row[1].replace('\n', ' ').replace('\r', '')
                result.append(dict(zip(keys,row)))
            print city+" done"


    else:
        cursor.execute('SELECT city_name, comments FROM reviews WHERE city_name like "%s" limit 500'%(city))
        rows = cursor.fetchall()
        #Store return data from the SQL query
        result = []
        for row in rows:
            row = list(row)
            row[1] = unicodedata.normalize('NFKD', row[1]).encode('ascii','ignore')
            row[1] = row[1].replace('\n', ' ').replace('\r', '')
            result.append(dict(zip(keys,row)))

    # rows = cursor.fetchall()
    # #Store return data from the SQL query
    # result = []
    #
    #
    # # keys = ('city_name', 'comments')
    #
    # for row in rows:
    #     row = list(row)
    #     row[1] = unicodedata.normalize('NFKD', row[1]).encode('ascii','ignore')
    #     row[1] = row[1].replace('\n', ' ').replace('\r', '')
    #     result.append(dict(zip(keys,row)))

    json_data = json.dumps(result, indent=4, sort_keys=True, default=str)

    #Get the city information for 1 year
    return HttpResponse(json_data, content_type="application/json")


def CalendarSummary(request, city, nhood):
    """
    @Table Structure:
    +------------+------------+---------------+------------------------------------------------------+
    | city_name  | date       | average_price | neighbourhood                                          |
    +------------+------------+---------------+------------------------------------------------------+

    @Description:
    Calendar Summary will retrieve 365 days of average pricing data and events for a particular city based on a particular neighbourhood.
    If average pricing required only for city, then input to neighbourhood should be 'all'
    """

    print("doing a query on the database for city %s and neighborhood %s"%(city, nhood))

    #Ensure that the spaces cities are supported
    city = city.replace('_', ' ')
    nhood = nhood.replace('_', ' ')

    cursor = connection.cursor()

    if (nhood.lower() == 'all'):
        cursor.execute('SELECT calendar_summary.city_name, calendar_summary.date, calendar_summary.average_price, calendar_summary.neighbourhood, holiday_event.holiday, holiday_event.event FROM calendar_summary left JOIN holiday_event ON (calendar_summary.city_name = holiday_event.city and calendar_summary.date = holiday_event.date) where calendar_summary.city_name = "%s" and neighbourhood is null order by calendar_summary.date'%(city) )
        rows = cursor.fetchall()
        # cursor.execute('SELECT AVG(average_price) FROM calendar_summary WHERE city_name = "%s" and neighbourhood is null'%(city))
        # ap = cursor.fetchone()
        cursor.execute('SELECT AVG(average_price), MAX(average_price), MIN(average_price) FROM calendar_summary WHERE city_name = "%s" and neighbourhood is null'%(city))
        [ap, maxP, minP] = cursor.fetchone()
        cursor.execute('SELECT calendar_summary.date FROM calendar_summary WHERE average_price = "%s" and city_name = "%s" and neighbourhood is null'%(maxP, city))
        maxDate = cursor.fetchone()
        # cursor.execute('SELECT MIN(average_price) FROM calendar_summary WHERE city_name = "%s" and neighbourhood is null'%(city))
        # minP = cursor.fetchone()
        cursor.execute('SELECT calendar_summary.date FROM calendar_summary WHERE average_price = "%s" and city_name = "%s" and neighbourhood is null'%(minP, city))
        minDate = cursor.fetchone()
    else:
        cursor.execute('SELECT calendar_summary.city_name, calendar_summary.date, calendar_summary.average_price, calendar_summary.neighbourhood, holiday_event.holiday, holiday_event.event FROM calendar_summary left JOIN holiday_event ON (calendar_summary.city_name = holiday_event.city and calendar_summary.date = holiday_event.date) where calendar_summary.city_name = "%s" and neighbourhood = "%s" order by calendar_summary.date'%(city, nhood) )
        rows = cursor.fetchall()
        cursor.execute('SELECT AVG(average_price), MAX(average_price), MIN(average_price) FROM calendar_summary WHERE city_name = "%s" and neighbourhood = "%s"'%(city, nhood))
        [ap, maxP, minP] = cursor.fetchone()
        # cursor.execute('SELECT MAX(average_price) FROM calendar_summary WHERE city_name = "%s" and neighbourhood = "%s"'%(city, nhood))
        # maxP = cursor.fetchone()
        cursor.execute('SELECT calendar_summary.date FROM calendar_summary WHERE average_price = "%s" and city_name = "%s" and neighbourhood = "%s"'%(maxP, city, nhood))
        maxDate = cursor.fetchone()
        # cursor.execute('SELECT MIN(average_price) FROM calendar_summary WHERE city_name = "%s" and neighbourhood = "%s"'%(city, nhood))
        # minP = cursor.fetchone()
        cursor.execute('SELECT calendar_summary.date FROM calendar_summary WHERE average_price = "%s" and city_name = "%s" and neighbourhood = "%s"'%(minP, city, nhood))
        minDate = cursor.fetchone()
        # 'SELECT * FROM calendar_summary WHERE city_name="%s"'%(city))


    print(ap)

    #Store return data from the SQL query
    result = []

    #Column values in the summary table
    keys = ('city_name','date', 'average_price', 'neighbourhood', 'holiday', 'event')

    for row in rows:
        result.append(dict(zip(keys,row)))

    # print(result)
    # avgP = []
    # keyP = ('avgP')
    # avgP.append(dict(zip(keyP, ap)))
    #
    # print(avgP)
    # avgPrice = json.loads(avgP)
    # dataPoints = json.loads(result)

    finaldata = { 'avgPrice' : ap, 'maxPrice' : maxP, 'maxDate' : maxDate[0], 'minDate' : minDate[0],'minPrice' : minP, 'dataPoints' : result }



    # finaldata = {'avgPrice': avgPrice['data'], 'dataPoints': dataPoints['data']}
    # print(finaldata)
    # mainKeys = ('averagePrice', 'dataPoints')
    #
    # final_json = []
    # final_json.append(dict(zip(mainKeys[0], avgP )))
    # final_json.append(dict(zip(mainKeys[1], result)))

    json_data = json.dumps(finaldata, indent=4, sort_keys=True, default=str)

    # print(json_data)
    #Get the city information for 1 year
    return HttpResponse(json_data, status=200, content_type="application/json")
