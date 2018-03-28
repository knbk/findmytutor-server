from django.contrib.gis.geos import Point
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance, DistanceField
import django_filters as filters

from .models import Tutor, Location

class TutorFilterSet(filters.FilterSet):
    hourly_rate = filters.NumberFilter(field_name='hourly_rate', lookup_expr='lte')
    subject = filters.CharFilter(method='filter_subject')
    rating = filters.NumberFilter(method='filter_rating')
    level = filters.ChoiceFilter(Tutor.LEVEL_CHOICES, empty_label=None, method='filter_level')
    distance = filters.CharFilter(method='filter_distance')

    def filter_subject(self, queryset, name, value):
        return queryset.filter(subjects__contains=[value])

    def filter_rating(self, queryset, name, value):
        return queryset.filter(rating__gte=value)

    def filter_level(self, queryset, name, value):
        if value == Tutor.PHD:
            return queryset.filter(level=Tutor.PHD)
        if value == Tutor.MASTER:
            return queryset.filter(level__in=[Tutor.MASTER, Tutor.PHD])
        if value == Tutor.BACHELOR:
            return queryset.filter(level__in=[Tutor.BACHELOR, Tutor.MASTER, Tutor.PHD])
        return queryset

    def filter_distance(self, queryset, name, value):
        try:
            longitude, latitude = map(float, value.split(',', 1))
        except ValueError:
            return queryset
        point = Point(longitude, latitude, srid=4326)
        return queryset.filter(
            locations__location__distance_lte=(point, Distance(km=10)),
        ).annotate(
            distance=models.Subquery(
                Location.objects.filter(tutors__id=models.OuterRef('pk')).annotate(
                    distance=Distance('location', point)
                ).values('distance').order_by('distance')[:1],
                output_field=models.DistanceField(),
            ),
        )

    class Meta:
        model = Tutor
        fields = ['hourly_rate', 'subject', 'rating', 'level', 'distance']
