from ..models import *
from ..serializers import *

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class ListModelsClass(APIView):
    http_method_names = ['get']

    def get(self, request: Request, *args, **kwargs):
        models_set = ModelsClass.objects.all()
        serializer = ModelsClassSerializer(instance=models_set, many=True)

        response_data = {
                "message": "models",
                "data": serializer.data
        }
        return Response(data=response_data, status=status.HTTP_200_OK)




class SaveModel(APIView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        model_name = request.data.get('modelName', '')
        location  = request.data.get('location', '')
        comment = request.data.get('comment', '')

        if ModelsClass.objects.filter(models_name=model_name).exists():
            return Response({'status': 'error', 'message': 'Name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        model = ModelsClass.objects.create(models_name=model_name,models_location=location, description=comment)
        serializer = ModelsClassSerializer(instance=model)
        response_data = {
            'status': 'success',
            'data': serializer.data,
            'models_id': model.models_id
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


