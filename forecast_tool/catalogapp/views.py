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
import pandas as pd

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
        print(main_data_event)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Events1.csv'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Name', 'Action', 'Value', 'Category'])
        writer.writerow(['test', 'test', 'test', 'test', 'test', 'test'])

        for row in main_data_event:
            five_digit_number = convert_date_to_five_digit_number(row.date_time)
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



class Test(APIView):
    trend_set_name = 'вфысфысс'
    trend = TrendsClass.objects.get(trends_set_name=trend_set_name)
    trend_set_id = trend.trends_set_id
    main_data_trend = MainClass.objects.filter(
    data_source_type=MainClass.TRENDS, 
    data_source_id=trend_set_id).values(
    'object_instance_id',  # This will keep object_instance_id
    'value',
    'object_type_property'# Other fields you want to keep
    )

    # Convert list of dictionaries into a DataFrame
    main_df = pd.DataFrame(list(main_data_trend))
    
    # Fetch object_instance_name separately
    object_instance_data = ObjectInstance.objects.values('object_instance_id', 'object_instance_name')
    object_type_property = ObjectTypeProperty.objects.values('object_type_property_id', 'object_type_property_name')
    
    # Convert object_instance_data into a dictionary for faster lookup
    object_instance_dict = {obj['object_instance_id']: obj['object_instance_name'] for obj in object_instance_data}
    object_property_dict = {obj['object_type_property_id']: obj['object_type_property_name'] for obj in object_type_property}
    
    # Replace object_instance_id with object_instance_name in main_df
    main_df['object_instance_name'] = main_df['object_instance_id'].map(object_instance_dict)
    main_df['object_type_property'] = main_df['object_type_property'].map(object_property_dict)
    print(main_df)
    main_df.rename(columns={'object_instance_name': 'Well_name'}, inplace=True)
    # Define the desired order of object_type_property values
    desired_order = [
        'GOR_Date', 'GOR_Initial', 'GOR_Slope',
        'c6_gor', 'c5_gor', 'c4_gor', 'c3_gor', 'c2_gor',
        'SBHP_Date', 'SBHP_Initial', 'SBHP_Slope',
        'c6_sbhp', 'c5_sbhp', 'c4_sbhp', 'c3_sbhp', 'c2_sbhp',
        'WCT_Date', 'WCT_Initial', 'WTC_Slope',
        'WCT_SI_Criteria', 'WCT_Delay',
        'PI_C_Date', 'c6_PI', 'c5_PI', 'c4_PI', 'c3_PI', 'c2_PI', 'c1_PI', 'c0_PI'
    ]

    # Convert 'object_type_property' to categorical with desired order
    main_df['object_type_property'] = pd.Categorical(main_df['object_type_property'], categories=desired_order, ordered=False)
    # Pivot the DataFrame
    pivot_data = main_df.pivot_table(index='Well_name', columns='object_type_property', values='value')
    # Reset the index to make 'object_instance_name' a regular column
    pivot_data.reset_index(inplace=True)

    print(pivot_data)

   
    pivot_data.to_csv('formatted_file.csv', index=False)





# class Test(APIView):
#     trend_set_name = 'tesy6'
#     trend = TrendsClass.objects.get(trends_set_name=trend_set_name)
#     trend_set_id = trend.trends_set_id
    
#     main_data_trend = MainClass.objects.filter(data_source_type=MainClass.TRENDS, data_source_id=trend_set_id)
    
#     # Получаем данные из ObjectInstance
#     object_instance_data = ObjectInstance.objects.all().values('object_instance_id', 'object_instance_name')
#     object_instance_dict = {item['object_instance_id']: item['object_instance_name'] for item in object_instance_data}

#     # Создаем словарь, содержащий для каждого типа данных (GOR, SBHP и т. д.) список столбцов
#     columns_dict = {
#         'GOR': ['GOR_Date', 'GOR_Initial', 'GOR_Slope', 'c6_gor','c5_gor','c4_gor','c3_gor','c2_gor'],
#         'SBHP': ['SBHP_Date', 'SBHP_Initial', 'SBHP_Slope', 'c6_sbhp','c5_sbhp','c4_sbhp','c3_sbhp','c2_sbhp'],
#         'Watercut': ['WCT_Date', 'WCT_Initial', 'WTC_Slope', 'WCT_SI_Criteria','WCT_Delay'],
#         'PI': ['PI_C_Date', 'c6_PI','c5_PI','c4_PI','c3_PI','c2_PI','c1_PI','c0_PI']
#     }

#     # Создаем список столбцов для DataFrame
#     columns = ['object_instance_id']
#     for columns_list in columns_dict.values():
#         columns.extend(columns_list)

#     # Создаем список значений для каждого объекта и добавляем его в список
#     main_data_list = []
#     for item in main_data_trend:
#         data_dict = {
#             'object_instance_id': object_instance_dict.get(item.object_instance_id, ''),
#             # Добавьте другие поля из MainClass, если необходимо
#         }
#         main_data_list.append(data_dict)
#     print(main_data_list)
#     # Создаем DataFrame из списка данных
#     main_df = pd.DataFrame(main_data_list)

#     # Если столбец 'object_instance_name' отсутствует в main_data_trend, добавьте его вручную
#     # main_df['object_instance_name'] = ...

#     # Группируем данные по object_instance_name и агрегируем значения value
#     transformed_df = main_df.groupby('object_instance_id')['value'].apply(list).reset_index()

#     # Если нужно, заменяем пустые значения в столбце 'value' на пустой список
#     transformed_df['value'] = transformed_df['value'].apply(lambda x: x if isinstance(x, list) else [])

#     # Разделяем значения value в отдельные столбцы
#     df = transformed_df.join(transformed_df['value'].apply(pd.Series).add_prefix('value'))
#     df.drop('value', axis=1, inplace=True)

# # Выводим DataFrame и сохраняем его в CSV файл
#     print(df)
#     df.to_csv('Trends1.csv', index=False)