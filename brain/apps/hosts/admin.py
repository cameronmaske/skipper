from django.contrib import admin
from hosts.models import Host


class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'ssh_setup')
    search_fields = ('name', 'host', 'port')


admin.site.register(Host, HostAdmin)
