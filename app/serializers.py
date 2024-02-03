from rest_framework import serializers

from .models import *


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('name',)


class PermitsSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True, many=False)
    moderator = UserSerializer(read_only=True, many=False)
    

    class Meta:
        model = Permit
        fields = "__all__"


class PermitSerializer(serializers.ModelSerializer):
    buildings = BuildingSerializer(read_only=True, many=True)
    owner = UserSerializer(read_only=True, many=False)
    moderator = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Permit
        fields = "__all__"


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'name')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            name=validated_data['name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)