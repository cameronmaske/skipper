from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from fabric.context_managers import settings

from hosts.api.serializer import HostSerializer
from hosts.models import Host
from ssh.helpers import get_private_key
from provisioner.setup import (
    install_core, has_docker, install_docker, docker_version, expose_docker)


class HostList(APIView):
    """
    /api/v1/hosts/
    GET: Lists all hosts.
    POST: Create a new host.
    """

    def get(self, request):
        hosts = Host.objects.all()
        serializer = HostSerializer(hosts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HostSerializer(data=request.DATA)

        if serializer.is_valid():
            host = serializer.object
            private_key = get_private_key()
            with settings(key=private_key, **host.env()):
                try:
                    install_core()
                    host.core_installed = True
                except Exception as e:
                    return Response("Core failed", status.HTTP_400_BAD_REQUEST)
                try:
                    if not has_docker():
                        install_docker()
                    host.docker_version = docker_version()
                    expose_docker()
                    host.docker_installed = True
                except Exception as e:
                    return Response("Docker failed", status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


host_list = HostList().as_view()


class HostDetail(APIView):
    """
    /api/v1/hosts/[pk]/
    GET: Returns a single host.
    POST: Update an existing host.
    """

    def get(self, request, pk):
        host = Host.objects.get(pk=pk)
        serializer = HostSerializer(host)
        return Response(serializer.data)

    def post(self, request, pk):
        host = Host.objects.get(pk=pk)
        serializer = HostSerializer(
            host, data=request.DATA, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

host_detail = HostDetail().as_view()
