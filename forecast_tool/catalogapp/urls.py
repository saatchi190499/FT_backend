from . import views
from django.urls import path
from .views import *
from .view.event_views import *
from .view.trend_views import *
from .view.model_views import *
from .view.server_views import *



urlpatterns = [
    path("models_set/",ListModelsClass.as_view(), name="models_set"),
    path("events_set_list/",ListEventsSet.as_view(), name="events_set_list"),
    path("trends_set_list/",ListTrendsSet.as_view(), name="trends_set_list"),
    path("sc_status_list/",ListScenarioStatusClass.as_view(), name="sc_status_list"),
    path("servers_list/",ListServersClass.as_view(), name="servers_list"),
    path("servers_create/",CreateServersClass.as_view(), name="servers_create"),

    path('save_model/', SaveModel.as_view(), name='save_model'),
    path('save_scenario/', SaveScenarioStatus.as_view(), name='save_scenario'),

    path('save_event/', SaveEvent.as_view(), name='save_event'),
    path('save_events/', SaveEventSet.as_view(), name='save_events'),

    path('save_trend/', SaveTrend.as_view(), name='save_trend'),
    path('save_trends/', SaveTrendSet.as_view(), name='save_trends'),

    path('export_scenario/', ExportScenario.as_view(), name='export_scenario'),
    path('run_scenario/', RunScenario.as_view(), name='run_scenario'),
    path('test/', Test.as_view(), name='test'),
    
    path('main_class/<str:select_events_set_id>/', CopyEventSet.as_view()),
    path('scenarios/<str:scenario_name>/', UpdateScenario.as_view(), name='update_scenario'),
]
