from django_filters import FilterSet, CharFilter, NumberFilter
from . models import Property

class PropertyFilter(FilterSet):
    type = CharFilter(field_name='type', lookup_expr='icontains')
    property_type = CharFilter(field_name='property_type', lookup_expr='icontains')
    
    class Meta:
        model = Property
        fields = ['type', 'property_type', 'city__id', 'price']