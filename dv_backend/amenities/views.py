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
from django.views.decorators.csrf import csrf_exempt
import math

@csrf_exempt
def AmenityData(request):

    '''
    @Description:
    Get average prices for each neighborhood in a specific city
    '''

    if (request.method == 'POST'):
        #List requested input params
        req_params = ['city_name', 'metric', 'filters']

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
        city_name, metric, filters = cleanse_input(post_dat)

        #Initialize the query that will get the pricing information based on the input information from the user into the SQL query
        cursor = connection.cursor()
        cursor.execute(retrieve_query(filters, city_name, amenities, metric))
        # rows = cursor.fetchall()
        rows = [list(item) for item in cursor.fetchall()]

        #This method is used to essentially parse the floats in a nicer way.. the indexing in the second loop is to handle neighborhoods
        for index1, row in enumerate(rows):
            for index2, value in enumerate(row[0:-1]):
                try:
                    row[index2] = float(value)
                    row[index2] = "{0:.2f}".format(row[index2])
                except Exception as e:
                    print(e)
                    continue

        #Store return data from the SQL query
        result = []
        
        #Column values in the summary table
        keys = ('percentDifference', 'averageWithCriteria', 'averageWithoutCriteria', 'totalAverage', 'neighborhood')

        for row in rows:
            result.append(dict(zip(keys,row)))

        #Compute the bin width for all values that are going to be classified
        bin_width, min_value, max_value = compute_bin_width(result)
        min_value = round(min_value, 2)

        for data in result:
    	    if (data['percentDifference'] is not None):
                correct_bin = -1
                data['percentDifference'] = float(data['percentDifference'])
                percent_difference_value = round(data['percentDifference'], 2)

                if (percent_difference_value is not None):
                    current_value = float(percent_difference_value)
                    correct_bin = determine_bin_placement(bin_width, current_value, min_value)
                    correct_bin = 7 if correct_bin > 7 else correct_bin or 1 if correct_bin < 1 else correct_bin
                    data['bin'] = int(correct_bin)

        final_json = {"Summary": {"min": "{0:.2f}".format(min_value), "interval": "{0:.2f}".format(bin_width)}, "Data": result}
        
        #Get the average pricing information based on filter selection
        return HttpResponse(json.dumps(final_json, indent=4, default=str), content_type="application/json", status=200)
    else:
        return HttpResponse("Get Req. Unsupported on Amenities", status=405)

def compute_bin_width(result):
    '''
    @Description:
    Compute the equal interval bin widths for the percentDifference
    '''
    #Max recommended number of bins to use for the equal interval classification
    NUMBER_OF_BINS = 7

    #Extract just the % difference values
    percent_difference_list = [pd['percentDifference'] for pd in result]
    percent_difference_list_updated = []

    #Cheap way of removing nils
    for data in percent_difference_list:
        if data != None:
            percent_difference_list_updated.append(data)

    #Compute all the values for the proper binning
    MIN_VALUE = min([float(i) for i in percent_difference_list_updated])
    MAX_VALUE = max([float(i) for i in percent_difference_list_updated])

    BIN_WIDTH = math.floor((MAX_VALUE - MIN_VALUE) / NUMBER_OF_BINS)

    BIN_WIDTH = 1 if BIN_WIDTH < 1 else BIN_WIDTH

    return BIN_WIDTH, MIN_VALUE, MAX_VALUE

def determine_bin_placement(bin_width, value, min_value):
    '''
    @Description:
    Places the incoming value for each neighborhood into it's associated return
    '''
    #Formula Used: CEILING(value - min)/bin_wdith
    return math.ceil((value - min_value) / bin_width)

def cleanse_input(post_dat):
    '''
    @Description:
    Clean the input data to process the SQL query
    '''
    city_name   = post_dat['city_name']
    metric      = post_dat['metric']
    filters = [x.strip(' ') for x in post_dat['filters'].split(',')]
    filters = ', '.join(filters)

    return city_name, metric, filters


def retrieve_query(filters, city, amenities, metric):
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
    ( ( avgWithCriteria - totalAverage ) / ( ( avgWithCriteria + totalAverage ) / 2 ) ) * 100 as percentDifference,
    a.*
FROM
    (SELECT
        AVG( CASE WHEN 'f' not in ( %s ) THEN %s ELSE null END) as avgWithCriteria,
        AVG( CASE WHEN 'f'        in ( %s ) THEN %s ELSE null END) as avgWithoutCriteria,
        AVG( %s ) as totalAverage,
        neighbourhood_cleansed
    FROM listings
    WHERE city_name = '%s'
    GROUP BY neighbourhood_cleansed ) a;
'''%(query_params, metric, query_params, metric, metric, city))
