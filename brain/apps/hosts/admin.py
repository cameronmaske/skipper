from django.contrib import admin
from hosts.models import Host


class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'port', 'core_installed', 'docker_installed', 'docker_version')
    search_fields = ('name', 'address', 'port')


admin.site.register(Host, HostAdmin)
