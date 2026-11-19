from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'),

    path(
        'booking/<int:booking_id>/',
        views.create_booking,
        name = "booking"
    ),

    path('profile/', views.profile, name='profile'),

    path('manager/', views.manager_panel, name='manager'),

    path(
        'manager/confirm/<int:booking_id>/',
        views.confirm_booking,
        name = "confirm_booking"
    ),

    path(
        'manager/issue/int:booking_id>/',
        views.issue_equipment,
        name = "issue_equipment"
    ),

    path(
        'manager/return/<int:booking_id>/',
        views.return_equipment,
        name = "return_equipment"
    ),

    path(
        'statistics/',
        views.statistics,
        name = "statistics"
    )
]