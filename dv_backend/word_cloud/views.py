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


def createWordCloudTables(request):

    """
    @Description:
    createWordCloudTables will create 2 tables word_frequency and word_tfidf to store cities, words and their respective frequencies/tfids from every review.

    """

    print("word_frequency table to be created.")
    detail = "000"
    try:
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE word_frequency \
                        (CITY varchar(255) NOT NULL, \
                        WORD varchar(255) NOT NULL,\
                        FREQUENCY int, \
                        CONSTRAINT PK_word_frequency PRIMARY KEY (CITY, WORD) \
                        );')

        connection.commit()

    except Exception as detail:
		print "OOPS! This is the error ==> ", detail


    print("word_tfidf table to be created.")
    try:
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE word_tfidf \
                        (CITY varchar(255) NOT NULL, \
                        WORD varchar(255) NOT NULL, \
                        TFIDF decimal(16, 12), \
                        CONSTRAINT PK_word_frequency PRIMARY KEY (CITY, WORD) \
                        );')

        connection.commit()

    except Exception as detail:
		print "OOPS! This is the error ==> ", detail


    return HttpResponse(detail)


def loadFrequencyTFIDF(request):

    """
    @Description:
    loadFrequencyTFIDF will load 2 tables word_frequency and word_tfidf to store cities, words and their respective frequencies/tfids from every review from a json file.

    """

    with open('/Users/suhasini/Desktop/cityFrequency300EnglishReviews.JSON'.decode('utf-8')) as json_data:
        json_obj = json.load(json_data)
    print(json_obj)

    city_name=''
    word_text=''
    frequency_size=0
    cursor = connection.cursor()

    for dataElement in json_obj["data"]:
        city_name = dataElement["city"]
        for i in dataElement['freqList']:
            word_text=i.get("text")
            frequency_size=i.get("size")
            cursor.execute("INSERT INTO word_frequency \
                                (city, word, frequency) \
                                VALUES (%s,%s,%s)", \
                                    (city_name, word_text, frequency_size))
            connection.commit()

        for j in dataElement['tfidfList']:
            word_tfidf=j.get("text")
            tfidf_size=j.get("size")
            cursor.execute("INSERT INTO word_tfidf \
                                 (city, word, tfidf) \
                                 VALUES (%s,%s,%s)", \
                                (city_name, word_tfidf, tfidf_size))
            connection.commit()



    return HttpResponse("check print")



def retrieveWordCloud(request, city):

    """
    @Description:
    retrieveWordCloud will retrieve from 2 tables word_frequency and word_tfidf to fetch cities, words and their respective frequencies/tfids and load into a json file.

    """
    cursor = connection.cursor()
    cursor.execute('SELECT word, frequency FROM word_frequency WHERE city = "%s"'%(city))
    freqs = cursor.fetchall();

    # cursor.execute('SELECT word, tfidf FROM word_tfidf WHERE city = "%s"'%(city))
    # tfidfs = cursor.fetchall();


    resultfreq = []
    # resulttfidf = []

    keys = ('text', 'size')

    for freq in freqs:
        resultfreq.append(dict(zip(keys,freq)))

    # for tfidf in tfidfs:
    #     resulttfidf.append(dict(zip(keys, tfidf)))

    # finaldata = { 'city' : city, 'freqList' : resultfreq, 'tfidfList' : resulttfidf }
    finaldata =  { 'freqList' : resultfreq }

    json_data = json.dumps(finaldata, indent=4, sort_keys=True, default=str)

    return HttpResponse(json_data, status=200, content_type="application/json")
