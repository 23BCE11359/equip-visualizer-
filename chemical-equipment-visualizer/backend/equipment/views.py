from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
import csv
import pandas as pd
from io import BytesIO

from .models import Equipment, Dataset
from .serializers import EquipmentSerializer, DatasetSerializer
from django.db.models import Count, Avg
from django.utils import timezone

try:
    # Optional dependency for PDF generation
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


class EquipmentViewSet(ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    search_fields = ['name']
    ordering_fields = [
        'name',
        'type',
        'material',
        'pressure',
        'temperature',
        'flowrate'
    ]

    filterset_fields = {
        'material': ['exact'],
        'pressure': ['gte'],
        'temperature': ['gte'],
        'type': ['exact'],
        'dataset': ['exact'],
    }


@api_view(['GET'])
def export_equipment_csv(request):
    qs = Equipment.objects.all()

    if request.GET.get('search'):
        qs = qs.filter(name__icontains=request.GET['search'])

    if request.GET.get('material'):
        qs = qs.filter(material=request.GET['material'])

    if request.GET.get('pressure__gte'):
        qs = qs.filter(pressure__gte=request.GET['pressure__gte'])

    if request.GET.get('temperature__gte'):
        qs = qs.filter(temperature__gte=request.GET['temperature__gte'])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="equipment.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Name',
        'Type',
        'Material',
        'Flowrate',
        'Pressure',
        'Temperature'
    ])

    for e in qs:
        writer.writerow([
            e.name,
            e.type,
            e.material,
            e.flowrate,
            e.pressure,
            e.temperature
        ])

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """Accept a CSV file, parse with pandas, create Dataset and Equipment rows. Requires authentication."""
    f = request.FILES.get('file')
    if not f:
        return Response({'detail': 'No file uploaded.'}, status=400)

    try:
        df = pd.read_csv(f)
    except Exception as e:
        return Response({'detail': f'Failed to parse CSV: {e}'}, status=400)

    # Normalize expected column names (case-insensitive)
    df.columns = [c.strip() for c in df.columns]

    name = getattr(f, 'name', f'upload-{timezone.now().isoformat()}')
    dataset = Dataset.objects.create(name=name)

    created = 0
    for _, row in df.iterrows():
        try:
            eq = Equipment.objects.create(
                dataset=dataset,
                name=row.get('Equipment Name') or row.get('name') or row.get('Name'),
                type=row.get('Type') or row.get('type') or '',
                flowrate=float(row.get('Flowrate') or 0),
                pressure=float(row.get('Pressure') or 0),
                temperature=float(row.get('Temperature') or 0),
                material=row.get('Material') or ''
            )
            created += 1
        except Exception:
            # skip bad rows
            continue

    serializer = DatasetSerializer(dataset, context={'request': request})
    return Response({'dataset': serializer.data, 'created': created})


@api_view(['GET'])
def datasets_list(request):
    """Return last 5 datasets with summary stats."""
    last5 = Dataset.objects.order_by('-uploaded_at')[:5]
    results = []
    for ds in last5:
        qs = ds.equipment.all()
        agg = qs.aggregate(
            count=Count('id'),
            avg_flowrate=Avg('flowrate'),
            avg_pressure=Avg('pressure'),
            avg_temperature=Avg('temperature')
        )
        types = list(qs.values('type').annotate(count=Count('id')))
        results.append({
            'id': ds.id,
            'name': ds.name,
            'uploaded_at': ds.uploaded_at,
            'equipment_count': agg['count'] or 0,
            'avg_flowrate': agg['avg_flowrate'] or 0,
            'avg_pressure': agg['avg_pressure'] or 0,
            'avg_temperature': agg['avg_temperature'] or 0,
            'type_distribution': {t['type']: t['count'] for t in types}
        })
    return Response(results)


@api_view(['GET'])
def dataset_summary(request, pk):
    try:
        ds = Dataset.objects.get(pk=pk)
    except Dataset.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=404)

    qs = ds.equipment.all()
    agg = qs.aggregate(
        count=Count('id'),
        avg_flowrate=Avg('flowrate'),
        avg_pressure=Avg('pressure'),
        avg_temperature=Avg('temperature')
    )
    types = list(qs.values('type').annotate(count=Count('id')))

    return Response({
        'id': ds.id,
        'name': ds.name,
        'uploaded_at': ds.uploaded_at,
        'equipment_count': agg['count'] or 0,
        'avg_flowrate': agg['avg_flowrate'] or 0,
        'avg_pressure': agg['avg_pressure'] or 0,
        'avg_temperature': agg['avg_temperature'] or 0,
        'type_distribution': {t['type']: t['count'] for t in types}
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_report_pdf(request, pk):
    """Generate a PDF report for a dataset with a tabular layout."""
    try:
        ds = Dataset.objects.get(pk=pk)
    except Dataset.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=404)

    if not REPORTLAB_AVAILABLE:
        return Response({'detail': 'PDF generation not available (reportlab missing).'}, status=501)

    # Build PDF using Platypus for nicer layout
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Dataset Report: {ds.name}", styles['Title']))
    story.append(Spacer(1, 12))

    qs = ds.equipment.all()
    agg = qs.aggregate(
        count=Count('id'),
        avg_flowrate=Avg('flowrate'),
        avg_pressure=Avg('pressure'),
        avg_temperature=Avg('temperature')
    )

    story.append(Paragraph(f"Uploaded: {ds.uploaded_at}", styles['Normal']))
    story.append(Paragraph(f"Equipment Count: {agg['count'] or 0}", styles['Normal']))
    story.append(Paragraph(f"Avg Flowrate: {round(agg['avg_flowrate'] or 0,2)}", styles['Normal']))
    story.append(Paragraph(f"Avg Pressure: {round(agg['avg_pressure'] or 0,2)}", styles['Normal']))
    story.append(Paragraph(f"Avg Temperature: {round(agg['avg_temperature'] or 0,2)}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Table header
    data = [["Name", "Type", "Flowrate", "Pressure", "Temperature"]]
    for e in qs:
        data.append([e.name, e.type, str(e.flowrate), str(e.pressure), str(e.temperature)])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#007bff')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))

    story.append(table)

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="dataset_{ds.id}.pdf"'
    return response
