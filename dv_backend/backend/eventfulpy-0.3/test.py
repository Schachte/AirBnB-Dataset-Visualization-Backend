#!/usr/bin/env python

import eventful

api = eventful.API('test_key', cache='.cache')
# api.login('username', 'password')
events = api.call('/events/search', q='music', l='San Diego')

for event in events['events']['event']:
    print "%s at %s" % (event['title'], event['venue_name'])
