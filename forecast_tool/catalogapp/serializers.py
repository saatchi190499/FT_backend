from rest_framework import serializers
from .models import *


class ModelsClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelsClass
        fields = ['models_id', 'models_name', 'created_date', 'models_location', 'description']

class TrendsClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendsClass
        fields = ['trends_set_id', 'trends_set_name', 'created_date', 'description']

class EventsClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsClass
        fields = ['events_set_id', 'events_set_name', 'created_date', 'description']

class ScenarioClassSerializer(serializers.ModelSerializer):
    models_id = serializers.SlugRelatedField(slug_field='models_name', queryset=ModelsClass.objects.all())
    trends_set_id = serializers.SlugRelatedField(slug_field='trends_set_name', queryset=TrendsClass.objects.all())
    events_set_id = serializers.SlugRelatedField(slug_field='events_set_name', queryset=EventsClass.objects.all())
    server = serializers.SlugRelatedField(slug_field='server_name', queryset=ServersClass.objects.all())

    class Meta:
        model = ScenarioClass
        fields = ['scenario_id', 'scenario_name', 'created_date', 'description', 'models_id', 'trends_set_id', 'events_set_id', 'status', 'server']

class ServersClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServersClass
        fields = '__all__'

class ObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectType
        fields = ['object_type_id', 'object_type_name']

class ObjectInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectInstance
        fields = ['object_instance_id', 'object_type', 'object_instance_name']

class ObjectTypePropertySerializer(serializers.ModelSerializer):
    # object_type = ObjectTypeSerializer()
    class Meta:
        model = ObjectTypeProperty
        fields = ['object_type_property_id', 'object_type', 'object_type_property_name', 'object_type_property_category']




class MainClassSerializer(serializers.ModelSerializer):
    object_type = serializers.SlugRelatedField(slug_field='object_type_name', queryset=ObjectType.objects.all())
    object_instance = serializers.SlugRelatedField(slug_field='object_instance_name', queryset=ObjectInstance.objects.all())
    # object_type_property = serializers.SlugRelatedField(slug_field='object_type_property_name', queryset=ObjectTypeProperty.objects.all())
    description = serializers.CharField(required=False)
    class Meta:
        model = MainClass
        fields = ['data_source_type', 'data_source_id', 'object_type', 'object_instance', 'object_type_property', 'value', 'date_time','sub_data_source','description']

class CopyMainClassSerializer(serializers.ModelSerializer):
    object_type = serializers.SlugRelatedField(slug_field='object_type_name', queryset=ObjectType.objects.all())
    object_instance = serializers.SlugRelatedField(slug_field='object_instance_name', queryset=ObjectInstance.objects.all())
    object_type_property = serializers.SlugRelatedField(slug_field='object_type_property_name', queryset=ObjectTypeProperty.objects.all())

    class Meta:
        model = MainClass
        fields = ['data_source_type', 'data_source_id', 'object_type', 'object_instance', 'object_type_property', 'value', 'date_time','sub_data_source','description']
