from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import TemplateView


def home(request):
    return HttpResponse("Backend running. Use /api/ for data.")

@api_view(['GET'])
def api_home(request):
    return Response({
        "project": "Chemical Equipment Parameter Visualizer",
        "status": "Backend API Running",
        "version": "1.0"
    })

urlpatterns = [
    # Serve the built frontend if available
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    path('status/', home),                  # status endpoint
    path('admin/', admin.site.urls),
    path('api/', api_home),                  # API home
    path('api/', include('equipment.urls')), # API endpoints
    path('api-token-auth/', obtain_auth_token),
]
