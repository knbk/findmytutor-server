from rest_framework import serializers

from .models import Meeting, Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['pk', 'rating', 'review']


class MeetingSerializer(serializers.ModelSerializer):
    is_accepted = serializers.BooleanField(read_only=True)
    is_cancelled = serializers.BooleanField(read_only=True)
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = Meeting
        fields = ['pk', 'tutor', 'student', 'start', 'end', 'location', 'is_accepted', 'is_cancelled', 'review']