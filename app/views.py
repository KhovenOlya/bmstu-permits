import requests
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .jwt_helper import *
from .permissions import *
from .serializers import *
from .utils import identity_user

from minio import Minio
import uuid
from django.shortcuts import get_object_or_404
from app.models import Building

Building.objects.filter(id__in=[13, 14, 15]).delete()

minio_client = Minio(endpoint="localhost:9000",   # адрес сервера
               access_key='minio',          # логин админа
               secret_key='minio124',       # пароль админа
               secure=False) 

def get_draft_permit(request):
    user = identity_user(request)

    if user is None:
        return None

    permit = Permit.objects.filter(owner_id=user.id).filter(status=1).first()

    return permit


@api_view(["GET"])
def search_buildings(request):
    query = request.GET.get("query", "")

    building = Building.objects.filter(status=1).filter(name__icontains=query)

    serializer = BuildingSerializer(building, many=True)

    draft_permit = get_draft_permit(request)

    resp = {
        "buildings": serializer.data,
        "draft_permit_id": draft_permit.pk if draft_permit else None
    }

    return Response(resp)


@api_view(["GET"])
def get_building_by_id(request, building_id):
    if not Building.objects.filter(pk=building_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    building = Building.objects.get(pk=building_id)
    serializer = BuildingSerializer(building, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_building(request, building_id):
    if not Building.objects.filter(pk=building_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    building = Building.objects.get(pk=building_id)
    serializer = BuildingSerializer(building, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_building(request):
    serializer = BuildingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_building(request, building_id):
    if not Building.objects.filter(pk=building_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    building = Building.objects.get(pk=building_id)
    building.status = 5
    building.save()

    building = Building.objects.filter(status=1)
    serializer = BuildingSerializer(building, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_building_to_permit(request, building_id):
    if not Building.objects.filter(pk=building_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    building = Building.objects.get(pk=building_id)

    permit = get_draft_permit(request)

    if permit is None:
        permit = Permit.objects.create()

    if permit.buildings.contains(building):
        return Response(status=status.HTTP_409_CONFLICT)

    permit.buildings.add(building)
    permit.owner = identity_user(request)
    permit.save()

    serializer = PermitSerializer(permit)
    return Response(serializer.data)


@api_view(["GET"])
def get_building_image(request, building_id):
    if not Building.objects.filter(pk=building_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    building = Building.objects.get(pk=building_id)

    return HttpResponse(building.image, content_type="image/png")

'''
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_building_image(request, building_id):
    if not Building.objects.filter(pk=building_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    building = Building.objects.get(pk=building_id)
    serializer = BuildingSerializer(building, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)
'''


api_view(["PUT"])
@permission_classes([IsModerator])
def update_building_image(request, pk):
    print ('kartinka')

    building = get_object_or_404(Building, pk=pk)

    serializer = BuildingSerializer(building, data=request.data, partial=True)
    if serializer.is_valid():
        img_name = str(uuid.uuid4())

        img_byte = request.data["image"]
        
        minio_client.put_object(
            bucket_name='images',  
            object_name=img_name,
            data=img_byte,
            length=len(img_byte)
        )

        serializer.validated_data['image'] = img_name
        serializer.save()

        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_permits(request):
    user = identity_user(request)

    status_id = int(request.GET.get("status", -1))
    date_start   = request.GET.get("date_start")
    date_end = request.GET.get("date_end")

    permits = Permit.objects.exclude(status__in=[1, 5])

    if not user.is_moderator:
        permits = permits.filter(owner=user)

    if status_id != -1:
        permits = permits.filter(status=status_id)

    if date_start  and isinstance(date_start , str):
        permits = permits.filter(date_formation__gte=parse_datetime(date_start ))

    if date_end and isinstance(date_end, str):
        permits = permits.filter(date_formation__lt=parse_datetime(date_end))

    serializer = PermitsSerializer(permits, many=True)

    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_permit_by_id(request, permit_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit = Permit.objects.get(pk=permit_id)
    serializer = PermitSerializer(permit, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_permit(request, permit_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit = Permit.objects.get(pk=permit_id)
    serializer = PermitSerializer(permit, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsRemoteService])
def update_security_decision(request, permit_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit = Permit.objects.get(pk=permit_id)
    serializer = PermitSerializer(permit, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, permit_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    permit = Permit.objects.get(pk=permit_id)

    permit.status = 2
    permit.date_formation = timezone.now()
    permit.save()

    '''calculate_security_decision(permit_id)'''

    serializer = PermitSerializer(permit, many=False)

    return Response(serializer.data)


def calculate_security_decision(permit_id):
    data = {
        "permit_id": permit_id
    }

    requests.post("http://127.0.0.1:8080/security_decision/", json=data, timeout=3)



@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, permit_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    permit = Permit.objects.get(pk=permit_id)

    if permit.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    permit.status = request_status
    permit.date_complete = timezone.now()
    permit.passege_date = timezone.now().date()
    permit.save()

    serializer = PermitSerializer(permit, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_permit(request, permit_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit = Permit.objects.get(pk=permit_id)

    if permit.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    permit.status = 5
    permit.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_building_from_permit(request, permit_id, building_id):
    if not Permit.objects.filter(pk=permit_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Building.objects.filter(pk=building_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    permit = Permit.objects.get(pk=permit_id)
    permit.buildings.remove(Building.objects.get(pk=building_id))
    permit.save()

    if permit.buildings.count() == 0:
        permit.delete()
        return Response(status=status.HTTP_201_CREATED)

    serializer = PermitSerializer(permit)

    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        message = {"message": "invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(user.id)

    user_data = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token
    }

    return Response(user_data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    access_token = create_access_token(user.id)

    message = {
        'message': 'Пользователь успешно зарегистрирован!',
        'user_id': user.id,
        "access_token": access_token
    }

    return Response(message, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def check(request):
    token = get_access_token(request)

    if token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    if token in cache:
        message = {"message": "Token in blacklist"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    user = CustomUser.objects.get(pk=user_id)
    serializer = UserSerializer(user, many=False)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    access_token = get_access_token(request)

    if access_token not in cache:
        cache.set(access_token, settings.JWT["ACCESS_TOKEN_LIFETIME"])

    message = {
        "message": "Вы успешно вышли из аккаунта"
    }

    return Response(message, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_building_image(request, pk):
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

        serializer.validated_data['image'] = img_name
        serializer.save()

        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
