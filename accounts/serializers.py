from rest_framework import serializers

from .models import User, Student, Tutor, Profile, Location


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['city', 'street_address', 'zip_code', 'latitude', 'longitude']


class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    date_of_birth = serializers.DateField()
    gender = serializers.CharField()
    tutors = serializers.StringRelatedField(many=True)
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['username', 'date_of_birth', 'gender', 'tutors', 'locations']

    def create(self, validated_data):
        user = User.objects.get(username=validated_data.pop('username'))
        profile = Profile.objects.create(user=user, type=Profile.STUDENT, **validated_data)
        student = Student.objects.create(profile=profile)
        return student

    def update(self, instance, validated_data):
        profile = instance.profile
        user = profile.user
        user.username = validated_data.pop('username')
        user.save(update_fields=['username'])
        profile.date_of_birth = validated_data['date_of_birth']
        profile.gender = validated_data['gender']
        profile.save(update_fields=['date_of_birth', 'gender'])
