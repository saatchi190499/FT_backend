from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError

from django.db.models.signals import pre_save
from django.dispatch import receiver
# Create your models here.




class ModelsClass(models.Model):
    models_id = models.AutoField(primary_key=True)
    models_name = models.CharField("Models", max_length = 50)
    #created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_date =  models.DateTimeField(auto_now_add=True)
    models_location = models.CharField("Location", max_length = 150)
    description = models.TextField("Comments")

    def __str__(self) -> str:
        return self.models_name

    class Meta:
        ordering = ["-created_date"]

############ Trends ############

def initial_trends_set_id():
    last_id = TrendsClass.objects.aggregate(models.Max('trends_set_id'))['trends_set_id__max']
    if last_id is None:
        return 'TR1000001'  
    else:
        last_id_str = str(last_id)[2:]  
        return 'TR' + str(int(last_id_str) + 1)

class TrendsClass(models.Model):
    trends_set_id = models.CharField(primary_key=True, max_length=50, default=initial_trends_set_id, editable=False)
    trends_set_name = models.CharField("Trends", max_length = 50)    
    # created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField("Comments")

    def save(self, *args, **kwargs):
        if not self.trends_set_id.startswith('TR'):
            self.trends_set_id = initial_trends_set_id()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.trends_set_name

    class Meta:
        ordering = ["-created_date"]


############ Events ############
def initial_events_set_id():
    last_id = EventsClass.objects.aggregate(models.Max('events_set_id'))['events_set_id__max']
    if last_id is None:
        return 'EC1000001' 
    else:
        last_id_str = str(last_id)[2:]  
        return 'EC' + str(int(last_id_str) + 1)


 
class EventsClass(models.Model):
    events_set_id = models.CharField(primary_key=True, max_length=50, default=initial_events_set_id, editable=False) 
    events_set_name = models.CharField("EventSet", max_length = 50) 
    #created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_date =  models.DateTimeField(auto_now_add=True)
    description = models.TextField("Comments")

    
    def __str__(self) -> str:
        return self.events_set_name

    class Meta:
        ordering = ["-created_date"]


class ServersClass(models.Model):
    server_id = models.AutoField(primary_key=True)
    server_name = models.CharField( max_length = 50)
    server_url = models.CharField( max_length = 250)
    server_status = models.CharField( max_length = 50)
    description = models.TextField("Description")

    def __str__(self) -> str:
        return self.server_name

    class Meta:
        ordering = ["-server_id"]

############ Scenario ############
def initial_scenario_id():
    last_id = ScenarioClass.objects.aggregate(models.Max('scenario_id'))['scenario_id__max']
    if last_id is None:
        return 'SC1000001'
    else:
        last_id_str = str(last_id)[2:]  
        return 'SC' + str(int(last_id_str) + 1)

class ScenarioClass(models.Model):
    scenario_id = models.CharField(primary_key=True, max_length=50, default=initial_scenario_id, editable=False)#models.AutoField(primary_key=True)     # db_column='id'
    scenario_name = models.CharField("Scenario", max_length = 50)
    created_date =  models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey(User,related_name='created_by', on_delete=models.PROTECT)
    status = models.CharField(max_length=50)
    server = models.ForeignKey(ServersClass, on_delete=models.SET_NULL, null=True)
    description = models.TextField("Description")
    models_id = models.ForeignKey(ModelsClass,on_delete=models.CASCADE) # to_field='models_name', db_column='models_name'
    trends_set_id = models.ForeignKey(TrendsClass,on_delete=models.CASCADE) # trends_set_id
    events_set_id = models.ForeignKey(EventsClass,on_delete=models.CASCADE) # events_set_id
    # run_by = models.ForeignKey(User,related_name='Run_by', on_delete=models.PROTECT, blank=True, null=True)
    # scenario_config_id = models.AutoField(primary_key=True,blank=True, null=True)#таймстеп

    def save(self, *args, **kwargs):
        if not self.scenario_id.startswith('SC'):
            self.scenario_id = initial_scenario_id()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.scenario_name

    class Meta:
        ordering = ["-created_date"]





############### Objects ###############

def initial_object_type_id():
    last_id = ObjectType.objects.aggregate(models.Max('object_type_id'))['object_type_id__max']
    if last_id is None:
        return 1000001
    else:
        return last_id + 1

class ObjectType(models.Model):
    object_type_id = models.AutoField(primary_key=True, unique=True, default=initial_object_type_id)
    object_type_name = models.CharField("ObjectType", unique=True, max_length = 50)

    def __str__(self) -> str:
        return self.object_type_name

    class Meta:
        ordering = ["-object_type_id"]


def initial_object_instance_id():
    last_id = ObjectInstance.objects.aggregate(models.Max('object_instance_id'))['object_instance_id__max']
    if last_id is None:
        return 1000001
    else:
        return last_id + 1

class ObjectInstance(models.Model):
    object_instance_id = models.AutoField(primary_key=True, unique=True, default=initial_object_instance_id)
    object_type = models.ForeignKey(ObjectType, on_delete=models.CASCADE)
    object_instance_name = models.CharField("ObjectInstance", unique=True, max_length = 50)

    def __str__(self) -> str:
        return self.object_instance_name

    class Meta:
        ordering = ["-object_instance_id"]


def initial_object_type_property_id():
    last_id = ObjectTypeProperty.objects.aggregate(models.Max('object_type_property_id'))['object_type_property_id__max']
    if last_id is None:
        return 1000001
    else:
        return last_id + 1

class ObjectTypeProperty(models.Model):
    object_type_property_id = models.AutoField(primary_key=True, unique=True, default=initial_object_type_property_id)
    object_type = models.ForeignKey(ObjectType, on_delete=models.CASCADE)
    object_type_property_name = models.CharField("ObjectTypeProperty", max_length = 50)
    object_type_property_category = models.CharField("Cataloge", max_length = 50)

    def __str__(self) -> str:
        return self.object_type_property_name

    class Meta:
        unique_together = (("object_type", "object_type_property_name"),) # ???
        ordering = ["-object_type_property_id"]


############### Main ###############

class MainClass(models.Model):
    SCENARIO = 'SC'
    EVENTS = 'EV'
    TRENDS = 'TR'
    DATA_SOURCE_CHOICES = [
        (SCENARIO, 'ScenarioClass'),
        (EVENTS, 'EventsClass'),
        (TRENDS, 'TrendsClass'),
    ]

    data_source_type = models.CharField(max_length=2, choices=DATA_SOURCE_CHOICES)
    data_source_id = models.CharField(max_length=50)
    object_type = models.ForeignKey(ObjectType, on_delete=models.CASCADE)
    object_instance = models.ForeignKey(ObjectInstance, on_delete=models.CASCADE)
    object_type_property = models.ForeignKey(ObjectTypeProperty, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2, db_column='value', null=True)#decimal_places>
    date_time = models.CharField("Date", max_length=50, db_column='date',null=True)#models.DateField(null=True) 
    sub_data_source = models.CharField("Category", max_length = 50, null=True) # trends[GOR, SBHP, WC] 
    description = models.TextField("Description") # trends => coments



# проверкa существования id
    def save(self, *args, **kwargs):
        # проверка существование записи с заданным data_source_id
        if self.data_source_type == self.SCENARIO:
            if not ScenarioClass.objects.filter(scenario_id=self.data_source_id).exists():
                raise ValidationError("Scenario with id {} does not exist.".format(self.data_source_id))
        elif self.data_source_type == self.EVENTS:
            if not EventsClass.objects.filter(events_set_id=self.data_source_id).exists():
                raise ValidationError("Events with id {} does not exist.".format(self.data_source_id))
        elif self.data_source_type == self.TRENDS:
            if not TrendsClass.objects.filter(trends_set_id=self.data_source_id).exists():
                raise ValidationError("Trends with id {} does not exist.".format(self.data_source_id))

        super().save(*args, **kwargs)

    

    class Meta:
        ordering = ["-data_source_id"]

@receiver(pre_save, sender=MainClass)
def validate_object_instance(sender, instance, **kwargs):
    if instance.object_instance.object_type != instance.object_type:
        raise ValueError("Object instance must belong to the selected object type.")
    
