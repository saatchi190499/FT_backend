from ..models import *
from ..serializers import *

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


# Create EventSet
class SaveEvent(APIView):
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        event_name = request.data.get('eventName', '')
        comment = request.data.get('comment', '')
        choose_set = request.data.get('choose', '')

        if EventsClass.objects.filter(events_set_name=event_name).exists():
            return Response({'status': 'error', 'message': 'Name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if choose_set != '':   
            try:
                selected_event = EventsClass.objects.get(events_set_name=choose_set)
                choose_event_id = selected_event.events_set_id
            except EventsClass.DoesNotExist:
                return Response({'status': 'error', 'message': 'Selected event not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            event = EventsClass.objects.create(events_set_name=event_name, description=comment)      
            serializer = EventsClassSerializer(instance=event)
            response_data = {
                'status': 'success',
                'data': serializer.data,
                'events_set_id': event.events_set_id,
                'selected_event_id': choose_event_id 
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            event = EventsClass.objects.create(events_set_name=event_name, description=comment)
            serializer = EventsClassSerializer(instance=event)
            response_data = {
                'status': 'success',
                'data': serializer.data,
                'events_set_id': event.events_set_id
            }
            return Response(response_data, status=status.HTTP_201_CREATED)


# Copy EventSet to a New EventSet
class CopyEventSet(APIView):
    def get(self, request, select_events_set_id):
        try:
            main_class_objects = MainClass.objects.filter(data_source_id=select_events_set_id)
            serializer = CopyMainClassSerializer(main_class_objects, many=True)
            return Response(serializer.data)
        except MainClass.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# EventsSet list from db
class ListEventsSet(APIView):
    http_method_names = ['get']

    def get(self, request: Request, *args, **kwargs):
        events_set_list = EventsClass.objects.all()
        serializer = EventsClassSerializer(instance=events_set_list, many=True)

        response_data = {
                "message": "events",
                "data": serializer.data
        }
        return Response(data=response_data, status=status.HTTP_200_OK)


# Saving Events in EventSet to db

class SaveEventSet(APIView):    
    def post(self, request):
        data = request.data
        for item in data:
            item["data_source_type"] = "EV"
            if item["date_time"] in ['', None]:
                item["date_time"] = '30/12/1899'
            object_type_name = item.get("object_type")
            object_type_property_name = item.get("object_type_property")
            
            try:
                object_type = ObjectType.objects.get(object_type_name=object_type_name)
                object_type_property = ObjectTypeProperty.objects.filter(object_type=object_type, object_type_property_name=object_type_property_name).first()
                
                if object_type_property:
                    item["object_type_property"] = object_type_property.object_type_property_id
            except ObjectTypeProperty.MultipleObjectsReturned:
                return Response(data={"error": f"Multiple ObjectTypeProperty objects returned for name '{object_type_property_name}'"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MainClassSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "message": "Mains Added",
                "data": serializer.data
            }
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)