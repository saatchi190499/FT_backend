from ..models import *
from ..serializers import *

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


    
class ListServersClass(APIView):
    http_method_names = ['get']

    def get(self, request: Request, *args, **kwargs):
        server = ServersClass.objects.all()
        serializer = ServersClassSerializer(instance=server, many=True)

        response_data = {
                "message": "server",
                "data": serializer.data
        }
        return Response(data=response_data, status=status.HTTP_200_OK)
    

   
class CreateServersClass(APIView):
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        server_name = request.data.get('serverName', '')
        server_url = request.data.get('serverURL', '')
        comment = request.data.get('comment', '')
        server_status = request.data.get('statusServer', '')
        
        if ServersClass.objects.filter(server_name=server_name).exists():
            return Response({'status': 'error', 'message': 'Name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        srv = ServersClass.objects.create(server_name=server_name, server_url=server_url, server_status=server_status,description=comment)
        print(srv)
        serializer = ServersClassSerializer(instance=srv)
        response_data = {
            'status': 'success',
            'data': serializer.data,
            'scenario_id': srv.server_id
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
