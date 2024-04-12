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
from django.core.exceptions import ObjectDoesNotExist

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
        # Retrieve the chosen scenario name from the request
        choose_scenario_name = request.GET.get('chooseScenario')
        scenario = ScenarioClass.objects.get(scenario_name=choose_scenario_name)

        # Retrieve the scenario ID or another unique identifier from the scenario
        scenario_id = scenario.scenario_id  # Assuming the ScenarioClass object has an `id` attribute

        # Define the scenario-specific folder path
        scenario_folder_name = f"Scenario_{scenario_id}"  # You can customize the folder name format as needed
        scenario_folder_path = os.path.join('E:/ByteAllEnergy/Forecast', scenario_folder_name)

        # Define the source paths of the CSV files
        source_paths = ['TrendEvent/Event.csv', 'TrendEvent/Trend.csv']

        # Define the destination paths within the scenario-specific folder
        destination_paths = [
            os.path.join(scenario_folder_path, 'Event.csv'),
            os.path.join(scenario_folder_path, 'Trend.csv')
        ]

        # Create the scenario-specific folder if it does not already exist
        os.makedirs(scenario_folder_path, exist_ok=True)

        # Generate the event and trend CSV files
        self.get_event(scenario)
        self.get_trend(scenario)

        # Move the files from source paths to destination paths
        for source_path, destination_path in zip(source_paths, destination_paths):
            # Move the file using shutil.move()
            shutil.move(source_path, destination_path)
            print(f"File successfully moved from {source_path} to {destination_path}")

        print(f"All files for scenario '{scenario_id}' moved to {scenario_folder_path}")

    def get_event(self, scenario):
        try:
            # Экспорт event CSV
            event_set_name = scenario.events_set_id
            event = EventsClass.objects.get(events_set_name=event_set_name)
            event_set_id = event.events_set_id

            main_data_event = MainClass.objects.filter(data_source_type=MainClass.EVENTS, data_source_id=event_set_id).values(
            'date_time',
            'object_type',
            'object_instance',
            'object_type_property',
            'value',
            'sub_data_source'
            )

            df_event = pd.DataFrame(list(main_data_event))
            df_event.rename(columns={
                'date_time': 'Date',
                'object_type': 'Type',
                'object_instance': 'Name',
                'object_type_property': 'Action',
                'value': 'Value',
                'sub_data_source': 'Category'
            }, inplace=True)
        
            csv_file_path = 'TrendEvent/Event.csv'  # Specify the path where you want to save the CSV file
            df_event.to_csv(csv_file_path, index=False)
            print(f"Data saved to {csv_file_path}.")
               
        except ObjectDoesNotExist as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
                
    def get_trend(self, scenario):
        try:
            # Fetch trend based on scenario
            trend_set_name = scenario.trends_set_id
            trend = TrendsClass.objects.get(trends_set_name=trend_set_name)
            trend_set_id = trend.trends_set_id
    
            # Fetch main data for trend
            main_data_trend = MainClass.objects.filter(
                data_source_type=MainClass.TRENDS,
                data_source_id=trend_set_id
            ).values('object_instance_id', 'value', 'object_type_property')
    
            # Convert data to a DataFrame
            main_df = pd.DataFrame(list(main_data_trend))
    
            # Fetch object instance and property data for mapping
            object_instance_data = ObjectInstance.objects.values('object_instance_id', 'object_instance_name')
            object_type_property_data = ObjectTypeProperty.objects.values('object_type_property_id', 'object_type_property_name')
    
            # Convert object instance and property data to dictionaries for mapping
            object_instance_dict = {obj['object_instance_id']: obj['object_instance_name'] for obj in object_instance_data}
            object_property_dict = {obj['object_type_property_id']: obj['object_type_property_name'] for obj in object_type_property_data}
    
            # Map object_instance_id and object_type_property
            main_df['object_instance_name'] = main_df['object_instance_id'].map(object_instance_dict)
            main_df['object_type_property'] = main_df['object_type_property'].map(object_property_dict)
            
            # Rename column to 'Well_name'
            main_df.rename(columns={'object_instance_name': 'Well_name'}, inplace=True)
    
            # Define desired order of columns
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
            main_df['object_type_property'] = pd.Categorical(main_df['object_type_property'], categories=desired_order, ordered=True)
    
            # Pivot the DataFrame
            pivot_data = main_df.pivot_table(index='Well_name', columns='object_type_property', values='value')
    
            # Create a DataFrame with all column values as "test" and "test" under "Well_name" column
            test_row_values = ['test'] * len(desired_order)
            test_row_values.insert(0, 'test')  # Add 'test' as the first value for 'Well_name'
            test_row_df = pd.DataFrame([test_row_values], columns=['Well_name'] + desired_order)
    
            # Concatenate test row to pivot data
            pivot_data = pd.concat([test_row_df, pivot_data.reset_index()], ignore_index=True)
                               
            # Save the DataFrame to a CSV file
            csv_file_path = 'TrendEvent/Trend.csv'  # Specify the path for saving the CSV file
            pivot_data.to_csv(csv_file_path, index=False)
            print(f"Data saved to {csv_file_path}.")
                
        except ObjectDoesNotExist as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")



class RunScenario(APIView):
    def post(self, request, *args, **kwargs):
        try:
            run_scenario()  
            return Response({"message": "Scenario started successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Test(APIView):
    pass
   #trend_set_name = 'вфысфысс'
   #trend = TrendsClass.objects.get(trends_set_name=trend_set_name)
   #trend_set_id = trend.trends_set_id
   #main_data_trend = MainClass.objects.filter(
   #data_source_type=MainClass.TRENDS, 
   #data_source_id=trend_set_id).values(
   #'object_instance_id',  # This will keep object_instance_id
   #'value',
   #'object_type_property'# Other fields you want to keep
   #)
   #event_set_name = "test2"
   #event = EventsClass.objects.get(events_set_name=event_set_name)
   #event_set_id = event.events_set_id
   #
   #main_data_event = MainClass.objects.filter(data_source_type=MainClass.EVENTS, data_source_id=event_set_id).values(
   #    'date_time',
   #    'object_type',
   #    'object_instance',
   #    'object_type_property',
   #    'value',
   #    'sub_data_source'
   #)
   #print(main_data_event)
   #df_event = pd.DataFrame(list(main_data_event))
   #print(df_event)
   ## Convert list of dictionaries into a DataFrame
   #main_df = pd.DataFrame(list(main_data_trend))
   #
   ## Fetch object_instance_name separately
   #object_instance_data = ObjectInstance.objects.values('object_instance_id', 'object_instance_name')
   #object_type_property = ObjectTypeProperty.objects.values('object_type_property_id', 'object_type_property_name')
   #
   ## Convert object_instance_data into a dictionary for faster lookup
   #object_instance_dict = {obj['object_instance_id']: obj['object_instance_name'] for obj in object_instance_data}
   #object_property_dict = {obj['object_type_property_id']: obj['object_type_property_name'] for obj in object_type_property}
   #
   ## Replace object_instance_id with object_instance_name in main_df
   #main_df['object_instance_name'] = main_df['object_instance_id'].map(object_instance_dict)
   #main_df['object_type_property'] = main_df['object_type_property'].map(object_property_dict)
   #print(main_df)
   #main_df.rename(columns={'object_instance_name': 'Well_name'}, inplace=True)
   ## Define the desired order of object_type_property values
   #desired_order = [
   #    'GOR_Date', 'GOR_Initial', 'GOR_Slope',
   #    'c6_gor', 'c5_gor', 'c4_gor', 'c3_gor', 'c2_gor',
   #    'SBHP_Date', 'SBHP_Initial', 'SBHP_Slope',
   #    'c6_sbhp', 'c5_sbhp', 'c4_sbhp', 'c3_sbhp', 'c2_sbhp',
   #    'WCT_Date', 'WCT_Initial', 'WTC_Slope',
   #    'WCT_SI_Criteria', 'WCT_Delay',
   #    'PI_C_Date', 'c6_PI', 'c5_PI', 'c4_PI', 'c3_PI', 'c2_PI', 'c1_PI', 'c0_PI']
   ## Convert 'object_type_property' to categorical with desired order
   #main_df['object_type_property'] = pd.Categorical(main_df['object_type_property'], categories=desired_order, ordered=False)
   ## Pivot the DataFrame
   #pivot_data = main_df.pivot_table(index='Well_name', columns='object_type_property', values='value')
   ## Create a DataFrame with all column values as "test" and "test" under "Well_name" column
   #test_row_values = ['test'] * (len(desired_order))  # One less column as the first one is 'Well_name'
   #test_row_values.insert(0, 'test')  # Insert 'test' as the first value
   #test_row_df = pd.DataFrame([test_row_values], columns=['Well_name'] + desired_order)  # Exclude the 'Well_name' from desired_order
   #
   ## Concatenate the test_row_df with pivot_data
   #pivot_data = pd.concat([test_row_df, pivot_data.reset_index()])
   #
   #pivot_data.to_csv('formatted_file.csv', index=False)


   #print(pivot_data)
    




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