from ..models import *
from ..serializers import *
from ..utils_views import *

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

class ListTrendsSet(APIView):
    http_method_names = ['get']

    def get(self, request: Request, *args, **kwargs):
        trends_set_list = TrendsClass.objects.all()
        serializer = TrendsClassSerializer(instance=trends_set_list, many=True)

        response_data = {
                "message": "events",
                "data": serializer.data
        }
        return Response(data=response_data, status=status.HTTP_200_OK)


class SaveTrend(APIView):
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        trend_name = request.data.get('trendName', '')
        comment = request.data.get('comment', '')

        if TrendsClass.objects.filter(trends_set_name=trend_name).exists():
            return Response({'status': 'error', 'message': 'Name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        trend = TrendsClass.objects.create(trends_set_name=trend_name, description=comment)

        serializer = TrendsClassSerializer(instance=trend)
        print(trend.trends_set_id)
        response_data = {
            'status': 'success',
            'data': serializer.data,
            'trends_set_id': trend.trends_set_id
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

##################################
class SaveTrendSet(APIView):
    def post(self, request):
        data = request.data
        saved_objects = []
        print(data)
        for row in data:
            object_instance_name = row['object_instance']
            data_source_id = row['data_source_id']
            values = row['value']
            values[0] = convert_date_to_five_digit_number(values[0])
            sub_data_source = row['sub_data_source']
            description = row['description']

            object_type = ObjectType.objects.get(object_type_name='WELL')
            object_instance = ObjectInstance.objects.get(object_instance_name=object_instance_name)
            
            values = [float(val) for val in values]

            for index, value in enumerate(values):
                column_names = ['init_date', 'init_value', 'slope', 'c6', 'c5', 'c4', 'c3', 'c2']
                object_type_property = column_names[index]
                object_type_property = ObjectTypeProperty.objects.get(object_type_property_name=object_type_property)
                
                saved_objects.append({
                    'data_source_type': 'TR',
                    'data_source_id': data_source_id,
                    'object_type': object_type,
                    'object_instance': object_instance,
                    'object_type_property': object_type_property,
                    'value': value,
                    'date_time': 0,
                    'sub_data_source': sub_data_source,
                    'description': description
                })

        serializer = CopyMainClassSerializer(data=saved_objects, many=True)
        
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "message": "Mains Added",
                "data": serializer.data
            }
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)