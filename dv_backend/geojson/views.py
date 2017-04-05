from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
import json, ast

def GetGeoJson(request, city_name=''):
    '''Returns the GEOJson for a particular city'''
    
    if (not city_name):
        return HttpResponse("Missing City Name : %s"%(city_name), status=422)
    else:

        try:
            #Query DB for the GEOJson Data
            cursor = connection.cursor()
            cursor.execute('SELECT geojson from neighbourhood_shape where city_name="%s"'%(city_name))
            rows = cursor.fetchall()
            
            json_data = json.dumps(rows[0], indent=4, sort_keys=True, default=str)
            json_data = json.loads(json_data)
            
            return HttpResponse(json_data, status=200)
        except Exception as e:
            
            # TODO: Make these errors make more sense
            return HttpResponse(e, status=500)
        
