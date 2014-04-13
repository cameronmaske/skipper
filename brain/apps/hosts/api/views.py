from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from hosts.api.serializer import HostSerializer
from hosts.model import Host


class HostList(APIView):
    """
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
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


host_list = HostList().as_view()


class HostDetail(APIView):
    """
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
