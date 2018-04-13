
from django.db.transaction import atomic
from rest_framework import serializers


from accounts.serializers import LocationSerializer
from accounts.models import Location
from .models import Meeting, Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['pk', 'rating', 'review']


class MeetingSerializer(serializers.ModelSerializer):
    is_accepted = serializers.BooleanField(read_only=True)
    is_cancelled = serializers.BooleanField(read_only=True)
    review = ReviewSerializer(read_only=True)
    location = LocationSerializer()

    def validate(self, attrs):
        if attrs['start'] >= attrs['end']:
            raise serializers.ValidationError('Start date must be before end date')
        return attrs

    class Meta:
        model = Meeting
        fields = ['pk', 'tutor', 'student', 'start', 'end', 'location', 'is_accepted', 'is_cancelled', 'review']

    @atomic()
    def create(self, validated_data):
        validated_data['location'] = Location.objects.create(**validated_data.pop('location'))
        return super().perform_create(validated_data)

    @atomic()
    def update(self, instance, validated_data):
        location = validated_data.pop('location')
        LocationSerializer(instance.location, data=location).save()
        return super().update(instance, validated_data)
