from rest_framework import serializers

from .models import User, Student, Tutor, Profile, Location


class UserSerializer(serializers.ModelSerializer):
    pk = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'first_name', 'last_name']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['city', 'street_address', 'zip_code', 'latitude', 'longitude']


class StudentSerializer(serializers.ModelSerializer):
    pk = serializers.HyperlinkedIdentityField(view_name='student-detail')
    username = serializers.CharField(source='profile.user.username')
    date_of_birth = serializers.DateField(source='profile.date_of_birth')
    gender = serializers.CharField(source='profile.gender')
    tutors = serializers.StringRelatedField(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['pk', 'username', 'date_of_birth', 'gender', 'tutors', 'locations']

    def create(self, validated_data):
        user = User.objects.get(username=validated_data['profile'].pop('user')['username'])
        profile = Profile.objects.create(user=user, type=Profile.STUDENT, **validated_data['profile'])
        student = Student.objects.create(profile=profile)
        return student

    def update(self, instance, validated_data):
        profile = instance.profile
        user = profile.user
        user.username = validated_data['profile']['user']['username']
        user.save(update_fields=['username'])
        profile.date_of_birth = validated_data['profile']['date_of_birth']
        profile.gender = validated_data['profile']['gender']
        profile.save(update_fields=['date_of_birth', 'gender'])
        return instance
