from django.conf.urls import url, include
from rest_framework import routers
from backend import views as calendar_views
from amenities import views as amenity_views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # url(r'', views.Home),
    url(r'summaries/daily/(?P<city>\w+)/$', calendar_views.CalendarSummary),
    url(r'review/comments/(?P<city>\w+)/$', calendar_views.CityReviews),
    url(r'amenities/$', amenity_views.AmenityData),
]
