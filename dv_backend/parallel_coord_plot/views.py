from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
from bson import json_util
import unicodedata
import json, ast
import os
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def ParallelCoordData(request):

    '''
    @Description:
    Get listings for each criteria selected in a specific city
    '''

    if (request.method == 'POST'):
        #List requested input params
        req_params = ['city_name', 'neighborhood', 'filters']

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

        #Retrieve clenased information
        city_name, neighborhood, filters = cleanse_input(post_dat)

        #Initialize the query that will get the pricing information based on the input information from the user into the SQL query
        cursor = connection.cursor()
        cursor.execute(retrieve_query(filters, city_name, amenities, neighborhood))
        rows = cursor.fetchall()

        #Store return data from the SQL query
        result = []

        #Column values in the summary table
        keys = ('Price', 'Estimated Monthly Stay', 'Estimated Monthly Income')

        for row in rows:
            result.append(dict(zip(keys,row)))

        if (filters == ''):
            return HttpResponse(json.dumps(result, indent=4, default=str), content_type="application/json", status=200)

        #Get the average pricing information based on filter selection
        return HttpResponse(json.dumps(result, indent=4, sort_keys=True, default=str), content_type="application/json", status=200)
    else:
        return HttpResponse("Get Req. Unsupported on Amenities", status=405)

def cleanse_input(post_dat):
    '''
    @Description:
    Clean the input data to process the SQL query
    '''
    city_name   = post_dat['city_name']
    # metric      = post_dat['metric']
    neighborhood = post_dat['neighborhood']
    filters = [x.strip(' ') for x in post_dat['filters'].split(',')]
    filters = ', '.join(filters)

    return city_name, neighborhood, filters


def retrieve_query(filters, city, amenities, neighborhood):
    '''
    @Description:
    Retrieve SQL Query
    '''
    query_params = ''

    #null params
    if (not filters):
        query_params = 'city_name'
    else:
        query_params = filters

    if (not neighborhood):
        return ('''
                SELECT
                    price, reviews_per_month, est_monthly_income
                FROM
                    listings
                WHERE
                    city_name = '%s'
                AND
                    'f' not in ( %s );
                '''%(city, query_params))
    else:
        return ('''
                SELECT
                    price, reviews_per_month, est_monthly_income
                FROM
                    listings
                WHERE
                    city_name = '%s'
                AND
                    'f' not in ( %s )
                AND
                    neighbourhood_cleansed = '%s';
                '''%(city, query_params, neighborhood))
