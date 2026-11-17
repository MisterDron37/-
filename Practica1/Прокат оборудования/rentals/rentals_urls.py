from django.urls import path
from . import views, views_manager

urlpatterns = [
    path("catalog/", views.catalog, name="catalog"),
    path("book/<int:equipment_id>/", views.create_booking, name="create_booking"),
    path("my/", views.my_bookings, name="my_bookings"),
    path("manager/", views_manager.manager_queue, name="manager_queue"),
    path("manager/confirm/<int:booking_id>/", views_manager.confirm_booking,
         name="confirm_booking"),
    path("manager/issue/<int:booking_id>/", views_manager.issue_equipment,
         name="issue_equipment"),
    path("manager/return/<int:rental_id>/", views_manager.accept_return,
         name="accept_return"),
]
