from django.shortcuts import render

# Create your views here.
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


def updateBars(request):

    '''
    @Description:
    Get bar values for specified filters in a specific city
    '''
    if (request.method == 'POST'):
        #List requested input params
        req_params = ['city_name', 'metric', 'filters', 'min_price', 'max_price', 'min_staycount', 'max_staycount', 'min_est_monthly_income', 'max_est_monthly_income']

        amenities = [
            'host_is_superhost',
            'security_deposit',
            'cleaning_fee',
            'instant_bookable',
            'has_internet',
            'has_kitchen',
            'allows_pets',
            'has_free_parking',
            'has_pool',
            'has_gym',
            'has_tv',
            'pets_live_on_property',
            'allows_smoking',
            'has_washer_and_dryer'
        ]

        #Unicode cleanse
        post_dat  = ast.literal_eval(json.dumps(request.POST))

        #Validation on query
        if not all(params in post_dat for params in req_params):
            return HttpResponse("Missing Parameters", status=422)


        #Retrieve cleansed information
        city_name, metric, filters, min_price, max_price, min_staycount, max_staycount, min_est_monthly_income, max_est_monthly_income = cleanse_input(post_dat)

        #Initialize the query that will get the pricing information based on the input information from the user into the SQL query
        cursor = connection.cursor()
        cursor.execute(retrieve_query(filters, city_name, amenities, metric, float(max_price), float(min_price), float(max_staycount), float(min_staycount), float(max_est_monthly_income), float(min_est_monthly_income)))
        # rows = cursor.fetchall()
        rows = [list(item) for item in cursor.fetchall()]


        #Store return data from the SQL query
        result = []

        #Column values in the summary table
        keys = ('priceWithCriteria', 'priceWithoutCriteria', 'rpmWithCriteria', 'rpmWithoutCriteria', 'emiWithCriteria', 'emiWithoutCriteria', 'listingWithCriteria', 'listingWithoutCriteria')

        for row in rows:
            result.append(dict(zip(keys,row)))

        return HttpResponse(json.dumps(result, indent=4, sort_keys=True, default=str), content_type="application/json", status=200)
    else:
        return HttpResponse("Get Req. Unsupported on Amenities", status=405)


def cleanse_input(post_dat):
    '''
    @Description:
    Clean the input data to process the SQL query
    '''
    city_name   = post_dat['city_name']
    metric      = post_dat['metric']

    min_price = post_dat['min_price']
    max_price = post_dat['max_price']

    min_staycount = post_dat['min_staycount']
    max_staycount = post_dat['max_staycount']

    min_est_monthly_income = post_dat['min_est_monthly_income']
    max_est_monthly_income = post_dat['max_est_monthly_income']

    filters = [x.strip(' ') for x in post_dat['filters'].split(',')]
    filters = ', '.join(filters)

    return city_name, metric, filters, min_price, max_price, min_staycount, max_staycount, min_est_monthly_income, max_est_monthly_income


def retrieve_query(filters, city, amenities, metric, max_price, min_price, max_staycount, min_staycount, max_est_monthly_income, min_est_monthly_income):
    '''
    @Description:
    Retrieve SQL Query
    '''
    query_params = ''

    #null params
    if (not filters):
        query_params = ','.join(amenities)
    else:
        query_params = filters
    return ('''
SELECT
    AVG( CASE WHEN 'f' not in ( %s ) THEN price ELSE null END) as priceWithCriteria,
    AVG( price ) as priceAverage,
    AVG( CASE WHEN 'f' not in ( %s ) THEN reviews_per_month ELSE null END) as rpmWithCriteria,
    AVG( reviews_per_month ) as rpmAverage,
    AVG( CASE WHEN 'f' not in ( %s ) THEN est_monthly_income ELSE null END) as emiWithCriteria,
    AVG( est_monthly_income ) as emiAverage,
    SUM( CASE WHEN 'f' not in ( %s ) THEN 1 ELSE 0 END) as listingCountWithCriteria,
    SUM( 1 ) as listingCountTotal,
    city_name
FROM listings
WHERE city_name = "%s"
AND price <= %.2f
AND price >= %.2f
AND reviews_per_month <= %.2f
AND reviews_per_month >= %.2f
AND est_monthly_income <= %.2f
AND est_monthly_income >= %.2f;
'''%(query_params, query_params, query_params, query_params, city, max_price, min_price, max_staycount, min_staycount, max_est_monthly_income, min_est_monthly_income))
