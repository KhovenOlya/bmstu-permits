from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('', search_buildings),
    path('api/buildings/search/', search_buildings),  # GET
    path('api/buildings/<int:building_id>/', get_building_by_id),  # GET
    path('api/buildings/<int:building_id>/image/', get_building_image),  # GET
    path('api/buildings/<int:building_id>/update/', update_building),  # PUT
    path('api/buildings/<int:pk>/update_image/', update_building_image),  # PUT
    path('api/buildings/<int:building_id>/delete/', delete_building),  # DELETE
    path('api/buildings/create/', create_building),  # POST
    path('api/buildings/<int:building_id>/add_to_permit/', add_building_to_permit),  # POST

    # Набор методов для заявок
    path('api/permits/search/', search_permits),  # GET
    path('api/permits/<int:permit_id>/', get_permit_by_id),  # GET
    path('api/permits/<int:permit_id>/update/', update_permit),  # PUT
    path('api/permits/<int:permit_id>/update_security_decision/', update_security_decision),  # PUT
    path('api/permits/<int:permit_id>/update_status_user/', update_status_user),  # PUT
    path('api/permits/<int:permit_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/permits/<int:permit_id>/delete/', delete_permit),  # DELETE
    path('api/permits/<int:permit_id>/delete_building/<int:building_id>/', delete_building_from_permit), # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/register/", register),
    path("api/login/", login),
    path("api/check/", check),
    path("api/logout/", logout)
]
