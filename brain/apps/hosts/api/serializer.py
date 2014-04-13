from rest_framework import serializers

from hosts.models import Host


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
