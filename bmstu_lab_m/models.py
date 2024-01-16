from django.db import models

class User(models.Model): 
    user_id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=25) 
    surname = models.CharField(max_length=25) 
    name = models.CharField(max_length=25)
    birth_date = models.DateField(blank=False)
    passport_data = models.CharField(max_length=35)
    login = models.CharField(unique=True, max_length=35)
    password = models.CharField(unique=True, max_length=35)
    is_admin = models.BooleanField(blank=True, null=True)
    class Meta:
        db_table = "User"

class Building(models.Model): 
    build_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=40) 
    description = models.CharField(max_length=100) 
    img_url = models.CharField(max_length=100) 
    opening_hours = models.CharField(max_length=100)
    build_status = models.CharField(max_length=20, blank=True, null=True)
    class Meta:
        db_table = "Building"
    
class Permit(models.Model): 
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    permit_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=30, blank=True, null=True) # Статус заявки
    date_create = models.DateTimeField() # Дата создания заявки
    date_formation = models.DateTimeField(blank=True, null=True) # Дата формирования заявки
    passege_date = models.DateTimeField() # Дата прохождения
    date_end = models.DateTimeField() # Дата закрытия заявки
    admin = models.ForeignKey('User', models.DO_NOTHING, related_name='requests_admin_set', blank=True, null=True)
    security_decision = models.CharField(max_length=30, blank=True, null=True)
    class Meta:
        db_table = "Permit"
    
class Build_Permit(models.Model):
    permit = models.ForeignKey(Permit, models.DO_NOTHING, blank=True, null=True)
    build = models.ForeignKey(Building, models.DO_NOTHING, blank=True, null=True)
    
    class Meta:
        db_table = 'Build_Permit'
        unique_together = (('permit', 'build'))


















     

# Create your models here.
