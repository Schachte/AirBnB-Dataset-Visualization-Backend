from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse
from django.db import connection
from bson import json_util
import json
import os

def CalendarSummary(request, city):
    """
    @Table Structure:
    +------------+------------+---------------+------------------------------------------------------+
    | city_name  | date       | average_price | happenings                                           |
    +------------+------------+---------------+------------------------------------------------------+
    
    @Description:
    Calendar Summary will retrieve 365 days of average pricing data and events for a particular city
    """
    
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM calendar_summary")
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
