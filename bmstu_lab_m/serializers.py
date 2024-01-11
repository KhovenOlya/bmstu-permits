from rest_framework import serializers
from bmstu_lab_m.models import Building
from bmstu_lab_m.models import User 
from bmstu_lab_m.models import Permit
from bmstu_lab_m.models import Build_Permit

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
        'user_id',
        'role', 
        'surname',
        'name',
        'birth_date',
        'passport_data',
        'login',
        'password',
        'is_admin',
        ]

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = [
        'build_id',
        'title', 
        'description', 
        'img_url', 
        'opening_hours',
        ]
'''
 def get_image(self, obj):
        image_data = get_image_from_s3(obj.modeling_image_url)
        if image_data:
            return image_data
        return None
'''
class PermitSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.login', read_only=True)
    date_create = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    date_formation = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    passege_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    date_end = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    admin = serializers.CharField(source='user.login', read_only=True)

    class Meta:
        model = Permit
        fields = [
            'user',
            'permit_id',
            'status',
            'date_create',
            'date_formation',
            'passege_date',
            'date_end',
            'admin',
        ]

class Build_PermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Build_Permit
        fields = [
            'permit',
            'build',
        ] 