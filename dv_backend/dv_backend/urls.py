from django.conf.urls import url, include
from rest_framework import routers
from backend import views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'summaries/daily/(?P<city>\w+)/$', views.CalendarSummary),
    url(r'review/comments/(?P<city>\w+)/$', views.CityReviews),
]
