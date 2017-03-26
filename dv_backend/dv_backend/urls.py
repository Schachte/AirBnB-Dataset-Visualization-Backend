from django.conf.urls import url, include
from rest_framework import routers
from backend import views
from backend import event_holiday_APICall

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'summaries/daily/(?P<city>\w+)/$', views.CalendarSummary),
    url(r'tester/(?P<city>\w+)/$', views.SuhaTest),
    url(r'testCreateTable/$', event_holiday_APICall.createHolidayEventTable),
    url(r'testloadholiday/(?P<city>\w+)/$', event_holiday_APICall.loadHolidays),
    url(r'testloadevent/(?P<city>\w+)/$', event_holiday_APICall.loadEvents),
    url(r'testholidayevent/(?P<city>\w+)/(?P<date>\d+)/$', event_holiday_APICall.HolidayEvent),
]
