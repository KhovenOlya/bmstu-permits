from django.shortcuts import render, redirect
from datetime import date, datetime, timedelta
from django.utils import timezone
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
from minio import Minio
import uuid
import io
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
import json
import hashlib
import secrets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
import redis
from django.conf import settings
from rest_framework import status as drf_status

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


'''{
    "title": "kjhgkdjhgkdnnj",
    "img_url": "jhkjfokk",
    "description":"jhdjlklfhjdh",
    "opening_hours": "jgmlklgkg",
    "build_status": "В работе"

     
}
'''
from bmstu_lab_m.redis_view import (
    set_key,
    get_value,
    delete_value
)
def login_view_get(request, format=None):
    existing_session = request.COOKIES.get('session_key')
    if existing_session and get_value(existing_session):
        return Response({'user_id': get_value(existing_session)})
    return Response(status=status.HTTP_401_UNAUTHORIZED)


def check_user(request):
    response = login_view_get(request._request)
    if response.status_code == 200:
        user = User.objects.get(user_id=response.data.get('user_id').decode())
        return user.role == 'User'
    return False


def check_authorize(request):
    response = login_view_get(request._request)
    if response.status_code == 200:
        user = User.objects.get(user_id=response.data.get('user_id'))
        return user
    return None

def check_admin(request):
    response = login_view_get(request._request)
    if response.status_code == 200:
        user = User.objects.get(user_id=response.data.get('user_id'))
        return user.role == 'Admin'
    return False


@api_view(['POST'])
def registration(request, format=None):
    required_fields = ['role','surname', 'name', 'passport_data', 'login', 'password', 'birth_date' ]
    missing_fields = [field for field in required_fields if field not in request.data]

    if missing_fields:
        return Response({'Ошибка': f'Заполните все обязательные поля: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(login=request.data['login']).exists():
        return Response({'Ошибка': 'Пользователь с таким login уже существует'}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create(
        surname=request.data['surname'],
        name=request.data['name'],
        passport_data=request.data['passport_data'],
        login=request.data['login'],
        password=request.data['password'],
        role = request.data['role'],
        birth_date = request.data['birth_date'],
    )
    return Response(status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'login': openapi.Schema(type=openapi.TYPE_STRING, description='Логин пользователя'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль пользователя'),
        },
        required=['login', 'password'],
    ),
    responses={
        200: openapi.Response(description='Успешная авторизация', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'user_id': openapi.Schema(type=openapi.TYPE_INTEGER)})),
        400: openapi.Response(description='Неверные параметры запроса или отсутствуют обязательные поля'),
        401: openapi.Response(description='Неавторизованный доступ'),
    },
    operation_description='Метод для авторизации',
)

@api_view(['POST'])
def login_view(request, format=None):
    existing_session = request.COOKIES.get('session_key')
    if existing_session and get_value(existing_session):
        return Response({'user_id': get_value(existing_session)})
        '''return Response({'user_id': get_value(existing_session), 'session_key': existing_session})'''

    login_ = request.data.get("login")
    password = request.data.get("password")
    
    if not login_ or not password:
        return Response({'error': 'Необходимы логин и пароль'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(login=login_)
    except User.DoesNotExist:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if password == user.password:
        random_part = secrets.token_hex(8)
        session_hash = hashlib.sha256(f'{user.user_id}:{login_}:{random_part}'.encode()).hexdigest()
        set_key(session_hash, user.user_id)

        '''response = JsonResponse({'user_id': user.user_id, 'session_key': session_hash})'''
        response = JsonResponse({'user_id': user.user_id})
        response.set_cookie('session_key', session_hash, max_age=86400)
        return response

    return Response(status=status.HTTP_401_UNAUTHORIZED)
@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(description='Успешный выход', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING)})),
        401: openapi.Response(description='Неавторизованный доступ', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})),
    },
    operation_description='Метод для выхода пользователя из системы',
)
@api_view(['GET'])
def logout_view(request):
    session_key = request.COOKIES.get('session_key')

    if session_key:
        if not get_value(session_key):
            return JsonResponse({'error': 'Вы не авторизованы'}, status=status.HTTP_401_UNAUTHORIZED)
        delete_value(session_key)
        response = JsonResponse({'message': 'Вы успешно вышли из системы'})
        response.delete_cookie('session_key')
        return response
    else:
        return JsonResponse({'error': 'Вы не авторизованы'}, status=status.HTTP_401_UNAUTHORIZED)
    

def login_view_get(request, format=None):
    existing_session = request.COOKIES.get('session_key')
    if existing_session and get_value(existing_session):
        return Response({'user_id': get_value(existing_session)})
    return Response(status=status.HTTP_401_UNAUTHORIZED)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

minio_client = Minio(endpoint="localhost:9000",   # адрес сервера
               access_key='minio',          # логин админа
               secret_key='minio124',       # пароль админа
               secure=False)                # опциональный параметр, отвечающий за вкл/выкл защищенное TLS соединение

@swagger_auto_schema(method='get', Building_Permit="Get Building", responses={200: BuildingSerializer(many=True)})
@api_view(["GET"])  # Возвращает список корпусов
def get_building(request, format=None):
    # building_list = Building.objects.filter(build_status="Действует")
    title = request.GET.get('title', None)

    if title:
        building_list = Building.objects.filter(title=title, build_status="Действует")
    else:
        building_list = Building.objects.filter(build_status="Действует")

    serializer = BuildingSerializer(building_list, many=True)
    data = serializer.data
    print(data)
    return Response(serializer.data)

@swagger_auto_schema(method='get', Building_Permit="Get Detail Building", responses={200: BuildingSerializer()})
@api_view(["GET"])
def get_detail_building(request, pk, format=None):
    if not Building.objects.filter(pk=pk).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    build = Building.objects.get(pk=pk)
    serializer = BuildingSerializer(build, many=False)
    return Response(serializer.data)

@swagger_auto_schema(method='post', Building_Permit="Add Building", request_body=BuildingSerializer, responses={201: BuildingSerializer()})
@api_view(["Post"]) # Добавляет новую услугу
def add_building(request, format=None): 
    serializer = BuildingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='POST', Building_Permit="Add Building To Permit", request_body=PermitSerializer, responses={200: 'OK', 404: 'Ошибка. Такая запись уже существует.', 403: 'Нет доступа'})
@api_view(['POST'])
def add_building_to_permit(request, pk):
        try:
            permits = Permit.objects.filter(status='Черновик').latest('date_create')
            print('hhghg')
        except Permit.DoesNotExist:
                current_user = User.objects.get(user_id=1)
                permits = Permit.objects.create(
                status='Черновик',
                date_create=datetime.now(),
                passege_date=datetime.now() + timedelta(days=1), 
                date_end=datetime.now() + timedelta(days=2),  
                admin=current_user,
            )
                permits.save()
                print('bbfbfd')

        build_id = pk
        try:
            build = Building.objects.get(build_id=build_id)
            build_permit = Build_Permit.objects.get(permit=permits, build=build)
            return Response("Ошибка. Такая запись уже существует.")
        except Build_Permit.DoesNotExist:
            build_permit = Build_Permit(
                permit=permits,
                build=build,
            )
            build_permit.save()

        permit_list = Permit.objects.all()
        serializer = PermitSerializer(permit_list, many=True)
        return Response(serializer.data)

@swagger_auto_schema(method='PUT', Building_Permit="Alter Building", request_body=BuildingSerializer, responses={200: BuildingSerializer(), 400: 'Bad Request'})
@api_view(["PUT"]) #изменение
def alter_building(request, pk, format=None):
    building = get_object_or_404(Building, pk=pk)
    serializer = BuildingSerializer(building, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='DELETE', Building_Permit="Delete Building", responses={404: 'Page Not Found'})
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
class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает доступ только администраторам. Для всех остальных запросов только для чтения.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

@swagger_auto_schema(method='GET', Building_Permit="Get Permit", responses={200: PermitSerializer(many=True)})
@api_view(["GET"])
def get_permit(permit, format=None):
    user = check_authorize(permit)
    if not user:
        return Response(status=drf_status.HTTP_403_FORBIDDEN)
    
    date_formation = permit.GET.get('date_formation', None)
    status = permit.GET.get('status', None)
    if user.role == "admin":
        permit_objects = Permit.objects.filter(admin=user)
    
        permit = Permit.objects.all()
    else:
        # Создатель видит только свои заявки
        permit = Permit.objects.filter(user=user)

        if date_formation:
            permit = permit.filter(date_formation=date_formation)
        if status:
            permit = permit.filter(status=status)
        serializer = PermitSerializer(permit, many=True)
        return Response(serializer.data)
@swagger_auto_schema(method='GET', Building_Permit="Get Permit Detailed", responses={200: PermitSerializer(many=True)})
@api_view(["GET"])
def get_permit_detailed(request, permit_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit = Permit.objects.get(pk=permit_id)
    serializer = PermitSerializer(permit, many=False)

    # Получение связанных зданий    ``
    build_permit_objects = Build_Permit.objects.filter(permit=permit)
    building_objects = [build_permit.build for build_permit in build_permit_objects]

    building_serializer = BuildingSerializer(building_objects, many=True)

    # Добавление связанных зданий к сериализатору Permit
    serialized_data = serializer.data
    serialized_data['buildings'] = building_serializer.data

    return Response(serialized_data)


'''
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
'''
@swagger_auto_schema(method='PUT', Building_Permit="Update Status User", responses={200: 'OK', 404: 'Not Found', 400: 'Bad Request'})
@api_view(["PUT"])
def update_status_user(request, pk):
    if not Permit.objects.filter(pk=pk).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    permit_status = request.data.get("status")

    if permit_status != 'Черновик':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    permit = Permit.objects.get(pk=pk)
    permit.status = permit_status
    permit.save()

    serializer = PermitSerializer(permit, many=False)

    return Response(serializer.data)

@swagger_auto_schema(method='PUT', Building_Permit="Update Status Admin", responses={200: 'OK', 404: 'Not Found', 400: 'Bad Request'})
@api_view(["PUT"])
def update_status_admin(request, pk):
    if not Permit.objects.filter(pk=pk).exists():
        return Response({"error": "Разрешение с таким pk не найдено"}, status=status.HTTP_404_NOT_FOUND)

    permit_status = request.data.get("status")
     
    if permit_status not in ['Завершен', 'Отклонен']:
        return Response({"error": "Недопустимый статус"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    permit = Permit.objects.get(pk=pk)
    permit.status = permit_status
    permit.date_formation = datetime.now()
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
@swagger_auto_schema(method='DELETE', operation_summary="Delete Permit Building", responses={200: Build_PermitSerializer()}) 
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

@swagger_auto_schema(method='PUT', Building_Permit="Update img building", responses={200: 'OK', 404: 'Not Found', 400: 'Bad Request'})
@api_view(["PUT"])
def update_img_building(request, pk):
    building = get_object_or_404(Building, pk=pk)

    serializer = BuildingSerializer(building, data=request.data, partial=True)

    if serializer.is_valid():
        img_name = str(uuid.uuid4())

        img_byte = request.data["image"]
        
        minio_client.put_object(
            bucket_name='img',  
            object_name=img_name,
            data=img_byte,
            length=len(img_byte)
        )

        serializer.validated_data['img_url'] = img_name
        serializer.save()

        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@swagger_auto_schema(method='PUT', Building_Permit="Complete Permit", responses={200: PermitSerializer()})
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def complete_permit(request, permit_id, format=None):
    user = check_authorize(request)
    if not user:
        return Response(status=drf_status.HTTP_403_FORBIDDEN)

    try:
        permit = Permit.objects.get(permit_id=permit_id)
    except Permit.DoesNotExist:
        return Response(status=drf_status.HTTP_404_NOT_FOUND)

    # Проверяем, является ли пользователь создателем или модератором (администратором)
    if user.role == "admin":
        # Обновление полей и завершение заявки
        permit.status = "Завершено"
        permit.date_end = timezone.now()  # Пример обновления других полей
        permit.save()

        serializer = PermitSerializer(permit)
        return Response(serializer.data)
    elif permit.user == user:
        # Если пользователь - создатель, возвращаем ошибку 403
        return Response(status=drf_status.HTTP_403_FORBIDDEN)
    else:
        return Response(status=drf_status.HTTP_403_FORBIDDEN)
