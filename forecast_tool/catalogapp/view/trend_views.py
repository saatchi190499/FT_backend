from ..models import *
from ..serializers import *
from ..utils_views import *

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView



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


class SaveTrendSet(APIView):
    def post(self, request):
        data = request.data
        saved_objects = []
        
        for row in data:
            object_instance_name = row['object_instance']
            data_source_id = row['data_source_id']
            values = row['value']
            values[0] = convert_date_to_five_digit_number(values[0])
            
            if isinstance(values[4], str):
                values[4] = convert_date_to_five_digit_number(values[4])
            
            sub_data_source = row['sub_data_source']
            description = row['description']

            object_type = ObjectType.objects.get(object_type_name='WELL')
            object_instance = ObjectInstance.objects.get(object_instance_name=object_instance_name)
            print(values)
            values = [float(val) for val in values]
            print(data)
            # for index, value in enumerate(values):
            #     column_names = ['init_date', 'init_value', 'slope', 'c6', 'c5', 'c4', 'c3', 'c2']
            #     object_type_property = column_names[index]
            #     object_type_property = ObjectTypeProperty.objects.get(object_type_property_name=object_type_property)
                
            #     saved_objects.append({
            #         'data_source_type': 'TR',
            #         'data_source_id': data_source_id,
            #         'object_type': object_type,
            #         'object_instance': object_instance,
            #         'object_type_property': object_type_property,
            #         'value': value,
            #         'date_time': 0,
            #         'sub_data_source': sub_data_source,
            #         'description': description
            #     })
            for index, value in enumerate(values):
                object_type_property = None
                if sub_data_source == 'GOR':
                    column_names = ['GOR_Date', 'GOR_Initial', 'GOR_Slope', 'c6_gor','c5_gor','c4_gor','c3_gor','c2_gor']
                elif sub_data_source == 'SBHP':
                    column_names = ['SBHP_Date', 'SBHP_Initial', 'SBHP_Slope', 'c6_sbhp','c5_sbhp','c4_sbhp','c3_sbhp','c2_sbhp']
                elif sub_data_source == 'Watercut':
                    column_names = ['WCT_Date', 'WCT_Initial', 'WTC_Slope', 'WCT_SI_Criteria','WCT_Delay']
                elif sub_data_source == 'PI':
                    column_names = ['PI_C_Date', 'c6_PI','c5_PI','c4_PI','c3_PI','c2_PI','c1_PI','c0_PI']

                if index < len(column_names):
                    object_type_property = ObjectTypeProperty.objects.get(object_type_property_name=column_names[index])

                if object_type_property is not None:
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
















