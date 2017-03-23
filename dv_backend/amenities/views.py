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
        
        #Parse dict.
        city_name   = post_dat['city_name']
        metric      = post_dat['metric']
        filters = [x.strip(' ') for x in post_dat['filters'].split(',')]
        
        print(filters)
        
        #Build the filter query to only set values to true if that filter was selected
        filter_query = ''
        
        if (filters[0]!=''):
            for amenity in filters:
                filter_query += 'and %s = "t" '%(amenity)
                
                
            # use dataviz;
            # 
            # SELECT
            #     ( ( avgWithCriteria - totalAverage ) / ( ( avgWithCriteria + totalAverage ) / 2 ) ) * 100 as percentDifference,
            #     a.*
            # FROM
            #     (SELECT
            #         AVG( CASE WHEN 'f' not in ( has_internet ) THEN price ELSE null END) as avgWithCriteria,
            #         AVG( CASE WHEN 'f'        in ( has_internet) THEN price ELSE null END) as avgWithoutCriteria,
            #         AVG( price ) as totalAverage,
            #         neighbourhood_cleansed
            #     FROM listings 
            #     WHERE city_name = 'Brussels'
            #     GROUP BY neighbourhood_cleansed ) a;        
        #Execute SQL command
        cursor = connection.cursor()
        if (filter_query != ''):
            
            cursor.execute('''
SELECT
    ( ( avgWithCriteria - totalAverage ) / ( ( avgWithCriteria + totalAverage ) / 2 ) ) * 100 as percentDifference,
    a.*
FROM
    (SELECT
        AVG( CASE WHEN 'f' not in ( has_internet ) THEN price ELSE null END) as avgWithCriteria,
        AVG( CASE WHEN 'f'        in ( has_internet) THEN price ELSE null END) as avgWithoutCriteria,
        AVG( price ) as totalAverage,
        neighbourhood_cleansed
    FROM listings 
    WHERE city_name = 'Brussels'
    GROUP BY neighbourhood_cleansed ) a; 
            ''')
        else:
            cursor.execute('SELECT neighbourhood_cleansed, AVG(price) from listings where city_name = "%s" group by neighbourhood_cleansed;'%(city_name))
        rows = cursor.fetchall()

        #Store return data from the SQL query
        result = []
        
        #Column values in the summary table
        keys = ('percentDifference', 'averageWithCriteria', 'averageWithoutCriteria', 'totalAverage', 'neighborhood')
        
        for row in rows:
            result.append(dict(zip(keys,row)))
        
        json_data = json.dumps(result, indent=4, sort_keys=True, default=str)

        #Get the average pricing information based on filter selection
        return HttpResponse(json_data, content_type="application/json", status=200)
    else:
        return HttpResponse("Get Req. Unsupported on Amenities", status=405)
