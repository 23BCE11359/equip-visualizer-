from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from .models import Equipment, Dataset

class EquipmentSerializer(ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):
    equipment_count = serializers.IntegerField(read_only=True)
    avg_flowrate = serializers.FloatField(read_only=True)
    avg_pressure = serializers.FloatField(read_only=True)
    avg_temperature = serializers.FloatField(read_only=True)
    type_distribution = serializers.DictField(read_only=True)

    class Meta:
        model = Dataset
        fields = (
            'id', 'name', 'uploaded_at',
            'equipment_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'type_distribution'
        )
