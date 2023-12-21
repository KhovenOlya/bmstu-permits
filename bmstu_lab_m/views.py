from django.shortcuts import render, redirect
from datetime import date
from django.db import connection
from django.urls import reverse
from .models import *
from bmstu_lab_m import models
import psycopg2
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import *

'''  Select * from "Building" where build_statuss='удален' '''
'''
data ={'building': [
    {'id':0, 'title':'Главное здание','img_url':'../static/images/gz.png','description':'2-я Бауманская ул., 5, стр. 4', 'opening_hours': 'Режим работы: С 9:00 до 18:00'},
    {'id':1, 'title':'Учебно-лабораторный корпус','img_url':'../static/images/ulk_1.png','description':'Рубцовская наб., 2/18','opening_hours': 'Режим работы: С 9:00 до 17:30'},
    {'id':2, 'title':'Энергомашиностроительный корпус','img_url':'../static/images/energo.jpg','description':'Лефортовская наб., 1','opening_hours': 'Режим работы: С 9:00 до 17:30'},
    {'id':3, 'title':'Специальное машиностроение','img_url':'../static/images/sm_1.png','description':'Госпитальный пер., 10 ','opening_hours': 'Режим работы: С 9:00 до 18:00'},
    {'id':4, 'title':'Технологический корпус','img_url':'../static/images/ibm.jpg','description':'2-я Бауманская ул., 7 ','opening_hours': 'Режим работы: С 9:00 до 17:30'}
    ]}

    
  

def GetDetailedAboutPermit(request, id):
    #data_id = data.get('building')[id]
    return render(request, 'bmstu/permit.html', {
        'building': models.Building.objects.filter(build_id=id).first()
    })    
def FindBuild(request):
    build_name = request.GET.get('building') 

    if build_name:
        find = Building.objects.filter(title__icontains=build_name, build_status="Действует")
    else:
        build_name = request.session.get('build_name','')
        find = Building.objects.filter(build_status="Действует")
    return render(request, "bmstu/university.html", {'find': find, 'find_value': build_name})              

def DeleteBuild(build_id):
    conn = psycopg2.connect(dbname="web", host="localhost", user="postgres", password="1", port="5432")
    with conn.cursor() as cursor:
        build_n = 'UPDATE "Building" SET "build_status" = %s WHERE build_id = %s'
        cursor.execute(build_n, ['удален', build_id])
        conn.commit()   
            
def UpdateBuild(request, id):
    DeleteBuild(id)
    return redirect('Find_url')     
'''
@api_view(["Get"]) #Возвращает список корпусов 
def get_building(request, format=None):
    building_list = Building.objects.filter(build_status="В работе")
    serializer = BuildingSerializer(building_list, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def get_detail_building(request, pk, format=None):
    if not Building.objects.filter(pk=pk).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    build = Building.objects.get(pk=pk)
    serializer = BuildingSerializer(build, many=False)
    return Response(serializer.data)


@api_view(["Post"]) # Добавляет новую услугу
def add_building(request, format=None): 
    serializer = BuildingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_building_to_permit(request, pk):
    try: 
        permits = Permit.objects.filter( status='В работе').latest('date_create') 
    except Permit.DoesNotExist:
        permits = Permit(                             
            status='В работе',
            date_create=datetime.now(),
            user=user,
            )
        permit.save()
    permit_id = permits
    build = pk
    try:
        builds = Building.objects.get(build_id=pk)
        build = Build_Permit.objects.get(permit=permits, build=builds) # проверка есть ли такая м-м
        return Response(f"Ошибка. Такая запись уже существует.")
    except Build_Permit.DoesNotExist:
        permit_build = Build_Permit(                            # если нет, создаем м-м
            permit=permits, build=builds
        )
        permit_build.save()
    permitt = Permit.objects.all()  # выводим все заказы
    serializer = PermitSerializer(permitt, many=True)
    return Response(serializer.data)

@api_view(["PUT"]) #изменение
def alter_building(request, pk, format=None):
    building = get_object_or_404(Building, pk=pk)
    serializer = BuildingSerializer(building, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_building(request, pk):
    try:
        build = Building.objects.get(build_id=pk)
        build.build_status = "Удален"
        build.save()
        builds = Building.objects.filter(build_status="В работе")
        serializer = BuildingSerializer(builds, many=True)
        return Response(serializer.data)
    except Building.DoesNotExist:
        return Response({"error": f"Корпус с идентификатором {pk} не существует."}, status=status.HTTP_404_NOT_FOUND)
'''
Заявки - GET список (кроме удаленных и черновика), GET одна запись (поля заявки + ее услуги),
PUT изменение (если есть доп поля заявки), PUT сформировать создателем, PUT завершить/отклонить модератором, DELETE удаление '''
@api_view(["GET"])
def get_permit(request):
    permit = Permit.objects.exclude(status__in=['Удален'])
    serializer = PermitSerializer(permit, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def get_building_detailed(request, permit_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    permit = Permit.objects.get(pk=permit_id)
    serializer = PermitSerializer(permit, many=False)
    return Response(serializer.data)

@api_view(["PUT"])
def update_permit(request, pk):
    if not Permit.objects.filter(pk=pk).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    permit = Permit.objects.get(pk=pk)
    serializer = PermitSerializer(permit, data=request.data, many=False, partial=True)
    if serializer.is_valid():
        serializer.save()
    permit.status = 'В работе'
    permit.save()
    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, pk):
    if not Permit.objects.filter(pk=pk).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit_status = request.data.get("status")

    if permit_status != 'В работе':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    permit = Permit.objects.get(pk=pk)
    permit.status = permit_status
    permit.save()

    serializer = PermitSerializer(permit, many=False)

    return Response(serializer.data)

@api_view(["PUT"])
def update_status_admin(request, pk):
    if not Permit.objects.filter(pk=pk).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit_status = request.data.get("status")
     
    if permit_status != 'Завершен' and permit_status != 'Отклонен':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    permit = Permit.objects.get(pk=pk)
    permit.status = permit_status
    permit.save()

    serializer = PermitSerializer(permit, many=False)

    return Response(serializer.data)

@api_view(["DELETE"])
def delete_permit(request, pk):
    if not Permit.objects.filter(pk=pk).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit = Permit.objects.get(pk=pk)
    permit.status = 'Удален'
    permit.save()
    return Response(status=status.HTTP_200_OK)


'''
@api_view(["DELETE"])
def delete_building_from_permit(request, permit_id, build_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Building.objects.filter(pk=build_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit = Permit.objects.get(pk=permit_id)
    permit.building.remove(Building.objects.get(pk=build_id))
    permit.save()
    serializer = BuildingSerializer(permit.building, many=True)
    return Response(serializer.data)    

    '''  
@api_view(['DELETE'])                                
def DeletePermitBuilding(request, pk):
    if not Build_Permit.objects.filter(id=pk).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    permit_build = get_object_or_404(Build_Permit, id=pk)
    permit_build.delete()
    permit = permit_build.permit
    permit.save()
    permit_build = Build_Permit.objects.all()
    serializer = Build_PermitSerializer(permit_build, many=True)
    return Response(serializer.data)
