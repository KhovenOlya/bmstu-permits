from django.db import models

class User(models.Model): 
    user_id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=25) 
    surname = models.CharField(max_length=25) 
    name = models.CharField(max_length=25)
    birthDate = models.DateField(blank=False)
    login = models.CharField(unique=True, max_length=35)
    password = models.CharField(unique=True, max_length=35)
    class Meta:
        db_table = "User"

class Building(models.Model): 
    build_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=40) 
    description = models.CharField(max_length=100) 
    img_url = models.CharField(max_length=50) 
    opening_hours = models.CharField(max_length=100)
    build_statuss = models.CharField(max_length=20, blank=True, null=True)
    class Meta:
        db_table = "Building"
    
class Status(models.Model): 
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=30, blank=True, null=True) # Статус заявки
    date_create = models.DateTimeField() # Дата создания заявки
    date_formation = models.DateTimeField() # Дата формирования заявки
    date_end = models.DateTimeField() # Дата закрытия заявки
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    class Meta:
        db_table = "Status"
    
class Build_Status(models.Model):
    status = models.ForeignKey(Status, models.DO_NOTHING, blank=True, null=True)
    build = models.ForeignKey(Building, models.DO_NOTHING, blank=True, null=True)
    
    class Meta:
        db_table = 'Build_Status'
        unique_together = (('status', 'build'))




















     

# Create your models here.
