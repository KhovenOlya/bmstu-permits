from django.shortcuts import render, redirect
from datetime import date
from django.db import connection
from django.urls import reverse
from .models import *
from bmstu_lab_m import models
import psycopg2
'''
data ={'building': [
    {'id':0, 'title':'Главное здание','img_url':'../static/images/gz.png','description':'2-я Бауманская ул., 5, стр. 4', 'opening_hours': 'Режим работы: С 9:00 до 18:00'},
    {'id':1, 'title':'Учебно-лабораторный корпус','img_url':'../static/images/ulk_1.png','description':'Рубцовская наб., 2/18','opening_hours': 'Режим работы: С 9:00 до 17:30'},
    {'id':2, 'title':'Энергомашиностроительный корпус','img_url':'../static/images/energo.jpg','description':'Лефортовская наб., 1','opening_hours': 'Режим работы: С 9:00 до 17:30'},
    {'id':3, 'title':'Специальное машиностроение','img_url':'../static/images/sm_1.png','description':'Госпитальный пер., 10 ','opening_hours': 'Режим работы: С 9:00 до 18:00'},
    {'id':4, 'title':'Технологический корпус','img_url':'../static/images/ibm.jpg','description':'2-я Бауманская ул., 7 ','opening_hours': 'Режим работы: С 9:00 до 17:30'}
    ]}

    
 ''' 

def GetDetailedAboutPermit(request, id):
    #data_id = data.get('building')[id]
    return render(request, 'bmstu/permit.html', {
        'building': models.Building.objects.filter(build_id=id).first()
    })    
def FindBuild(request):
    build_name = request.GET.get('building') 

    if build_name:
        find = Building.objects.filter(title__icontains=build_name)
    else:
        build_name = ''
        find = Building.objects.all()
    return render(request, "bmstu/university.html", {'find': find, 'find_value': build_name})              

def DeleteBuild(build_id):
    conn = psycopg2.connect(dbname="rip", host="localhost", user="postgres", password="1", port="5432")
    with connection.cursor() as cursor:
        build_n = 'UPDATE "Building" SET "build_statuss" = %s WHERE build_id = %s'
        cursor.execute(build_n, ['удален', build_id])
        connection.commit()   # реальное выполнение команд sql1
            
def UpdateBuild(request, id):
    if not DeleteBuild(id):
        pass
    return redirect(reverse('Find_url'))