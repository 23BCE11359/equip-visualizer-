from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    EquipmentViewSet,
    export_equipment_csv,
    upload_csv,
    datasets_list,
    dataset_summary,
    dataset_report_pdf,
)

router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')

urlpatterns = router.urls + [
    path('equipment/export/csv/', export_equipment_csv),
    path('upload/', upload_csv),
    path('datasets/', datasets_list),
    path('datasets/<int:pk>/summary/', dataset_summary),
    path('datasets/<int:pk>/report/pdf/', dataset_report_pdf),
]
