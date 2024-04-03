from .models import *
from .serializers import *
import PetexRoutines as PE
import GAP_utils as ut
from .utils_views import *

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

import os, csv, shutil
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


class ListScenarioStatusClass(APIView):
    http_method_names = ['get']

    def get(self, request: Request, *args, **kwargs):
        scenario = ScenarioClass.objects.all()
        serializer = ScenarioClassSerializer(instance=scenario, many=True)

        response_data = {
                "message": "scenario",
                "data": serializer.data
        }
        return Response(data=response_data, status=status.HTTP_200_OK)
            

class SaveScenarioStatus(APIView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        scenario_name = request.data.get('statusScName', '')
        model_name = request.data.get('model', '')
        event_name = request.data.get('event', '')
        trend_name = request.data.get('trend', '')
        comment = request.data.get('comment', '')
        statusSC = 'created'

        if ScenarioClass.objects.filter(scenario_name=scenario_name).exists():
            return Response({'status': 'error', 'message': 'Name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            model_instance = ModelsClass.objects.get(models_name=model_name)
            event_instance = EventsClass.objects.get(events_set_name=event_name)
            trend_instance = TrendsClass.objects.get(trends_set_name=trend_name)
        except (ModelsClass.DoesNotExist, EventsClass.DoesNotExist, TrendsClass.DoesNotExist) as e:
            return Response({'status': 'error', 'message': 'One or more of the specified models, events, or trends do not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        scenario = ScenarioClass.objects.create(scenario_name=scenario_name,
                                                models_id=model_instance,
                                                events_set_id=event_instance,
                                                trends_set_id=trend_instance,
                                                status = statusSC,
                                                description=comment)

        serializer = ScenarioClassSerializer(instance=scenario)
        response_data = {
            'status': 'success',
            'data': serializer.data,
            'scenario_id': scenario.scenario_id
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class UpdateScenario(APIView):
    http_method_names = ['put']

    def put(self, request, scenario_name):
        server_name = request.data.get('server', '')
        
        scenario = get_object_or_404(ScenarioClass, scenario_name=scenario_name)
        
        server = get_object_or_404(ServersClass, server_name=server_name)
        
        scenario.status = 'running'
        scenario.server = server
        scenario.save()

        serializer = ScenarioClassSerializer(scenario)
        return Response(serializer.data)
    

class ExportScenario(APIView):
    
    def get(self, request, *args, **kwargs):
        # Экспорт CSV
        choose_scenario_name = request.GET.get('chooseScenario')
        scenario = ScenarioClass.objects.get(scenario_name=choose_scenario_name)
        
        event_set_name = scenario.events_set_id
        event = EventsClass.objects.get(events_set_name=event_set_name)
        event_set_id = event.events_set_id
        
        main_data_event = MainClass.objects.filter(data_source_type=MainClass.EVENTS, data_source_id=event_set_id)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Events1.csv'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Name', 'Action', 'Value', 'Category'])
        writer.writerow(['test', 'test', 'test', 'test', 'test', 'test'])

        for row in main_data_event:
            five_digit_number = convert_date_to_five_digit_number(row.date_time)
            print(row.date_time,five_digit_number)
            writer.writerow([
                five_digit_number,#row.date_time,
                row.object_type,
                row.object_instance,
                row.object_type_property,
                row.value,
                row.sub_data_source
            ])
        source_path = 'C:/Users/user/Downloads/Events1.csv'#'D:/Users/dospaa/Downloads/Events1.csv' #D:\Users\dospaa\Downloads
        destination_path = 'C:/Users/user/Documents/KPO/отчет/Report CallOff 4/Forecast/Events1.csv' #F:\ForecastTool\Resolve_29022024
        
        if os.path.exists(source_path):
            os.remove(source_path)  
        with open(source_path, 'wb') as file:
            file.write(response.getvalue())
        if os.path.exists(destination_path):
            os.remove(destination_path)  

        shutil.move(source_path, destination_path)  
        print(f"Файл успешно перемещен из {source_path} в {destination_path}")

        if os.path.exists(source_path):
            os.remove(source_path)
        return response


class RunScenario(APIView):
    def post(self, request, *args, **kwargs):
        try:
            run_scenario()  
            return Response({"message": "Scenario started successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


