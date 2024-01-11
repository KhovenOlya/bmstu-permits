"""
URL configuration for bmstu_lab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from bmstu_lab_m import views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('building/<int:id>/', views.GetDetailedAboutPermit, name='GetDetailedAboutPermit'),
    #path('', views.FindBuild, name='Find_url'),
    #path('update/<int:id>', views.UpdateBuild, name='UpdateBuild'),
    path('', views.get_building, name='get_building_list'),
    path('api/buildings/', views.get_building, name='get_building_list'),
    path('api/buildings/<int:pk>/', views.get_detail_building, name='get_detail_building'),
    path('api/buildings/add/', views.add_building, name='create_building'),
    path('api/buildings/add_to_permit/<int:pk>/', views.add_building_to_permit, name='add_building_to_permit'),
    path('api/buildings/alter/<int:pk>/', views.alter_building, name='alter_building'),
    path('api/buildings/delete/<int:pk>/', views.delete_building, name='delete_building'),

    path('api/permits/', views.get_permit, name='get_permit_list'),
    path('api/permits/<int:permit_id>/', views.get_permit_detailed, name='get_permit_detailed'),
    #path('api/permits/update/<int:pk>/', views.update_permit, name='update_permit'),   
    path('api/permits/update_status_user/<int:pk>/', views.update_status_user, name='update_status_user'),
    path('api/permits/update_status_admin/<int:pk>/', views.update_status_admin, name='update_status_admin'),
    path('api/permits/delete/<int:pk>/', views.delete_permit, name='delete_permit'),
    #path('api/delete_permit_build/', views.delete_building_from_permit, name='delete_building'),
    path('api/build_permits/delete/<int:pk>/', views.DeletePermitBuilding, name='delete_permit_building'),
    path('api/update_img_building/<int:pk>/', views.update_img_building, name='update_img_building'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/user/registration/', views.registration, name='registration'),
    path('api/user/login/', views.login_view, name='login'),
    path('api/user/logout/', views.logout_view, name='logout'),
    path('api/permits/<int:permit_id>/complete/', views.complete_permit, name='complete_permit'),


]





