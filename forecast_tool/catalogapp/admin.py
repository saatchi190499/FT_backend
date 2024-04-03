from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import *

# Register your models here.


@admin.register(ModelsClass)
class ModelsClassAdmin(admin.ModelAdmin):
    list_display = ('models_id', 'models_name', 'created_date', 'models_location', 'description')
    list_filter = ['models_id']

@admin.register(TrendsClass)
class TrendsClassAdmin(admin.ModelAdmin):
    list_display = ('trends_set_id', 'trends_set_name', 'created_date', 'description')
    list_filter = ['trends_set_id']

@admin.register(EventsClass)
class EventsClassAdmin(admin.ModelAdmin):
    list_display = ('events_set_id', 'events_set_name', 'created_date', 'description')
    list_filter = ['events_set_id']

@admin.register(ScenarioClass)
class ScenarioClassAdmin(admin.ModelAdmin):
    list_display = ('scenario_id', 'scenario_name', 'created_date', 
                    'description', 'models_id', 'trends_set_id', 'events_set_id', 'status', 'server')
    list_filter = ['scenario_id']

@admin.register(ServersClass)
class ServersClassAdmin(admin.ModelAdmin):
    list_display = ('server_id', 'server_name', 'server_url', 'server_status', 'description')
    list_filter = ('server_id',)

@admin.register(ObjectType)
class ObjectTypeAdmin(admin.ModelAdmin):
    list_display = ('object_type_id', 'object_type_name')
    list_filter = ['object_type_id']

@admin.register(ObjectInstance)
class ObjectInstanceAdmin(admin.ModelAdmin):
    list_display = ('object_instance_id', 'object_type', 'object_instance_name')
    list_filter = ['object_instance_id']

@admin.register(ObjectTypeProperty)
class ObjectTypePropertyAdmin(admin.ModelAdmin):
    list_display = ('object_type_property_id', 'object_type', 'object_type_property_name', 'object_type_property_category')
    list_filter = ['object_type_property_id']


@admin.register(MainClass)
class MainClassAdmin(admin.ModelAdmin):
    list_display = ('data_source_type', 'data_source_id', 'object_type', 'object_instance', 'object_type_property', 'value', 'date_time','sub_data_source','description')
    list_filter = ('data_source_type',)
