from django.conf.urls import patterns, url

urlpatterns = patterns(
    'hosts.api.views',
    url(r'^hosts/$', 'host_list', name='host_list'),
    url(r'^hosts/(?P<pk>\d+)/$', 'host_detail', name='host_detail'),
)