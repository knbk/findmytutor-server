from rest_framework import serializers

from .models import User, Student, Tutor, Profile, Location


class UserSerializer(serializers.ModelSerializer):
    # pk = serializers.HyperlinkedIdentityField(view_name='user-detail')
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        if password and not instance.check_password(password):
            instance.set_password(password)
        return super().update(instance, validated_data)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['pk', 'address', 'google_id', 'latitude', 'longitude']


class NestedTutorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    date_of_birth = serializers.DateTimeField(source='date_of_birth_datetime')
    gender = serializers.CharField()
    hourly_rate = serializers.DecimalField(10, 2)
    available = serializers.BooleanField()
    locations = LocationSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Tutor
        fields = ['pk', 'username', 'date_of_birth', 'gender', 'hourly_rate', 'subjects', 'available', 'locations', 'rating']


class StudentSerializer(serializers.ModelSerializer):
    # pk = serializers.HyperlinkedIdentityField(view_name='student-detail')
    username = serializers.CharField(source='user.username')
    date_of_birth = serializers.DateTimeField(source='date_of_birth_datetime')
    gender = serializers.CharField()
    tutors = NestedTutorSerializer(many=True, read_only=True)
    locations = LocationSerializer(many=True)

    class Meta:
        model = Student
        fields = ['pk', 'username', 'date_of_birth', 'gender', 'tutors', 'locations']

    def create(self, validated_data):
        locations = validated_data.pop('locations')
        user = validated_data['user']
        user.type = User.STUDENT
        user.save(update_fields=['type', 'username'])
        obj = super().create(validated_data)
        for location in locations:
            obj.locations.create(**location)
        return obj

    def update(self, instance, validated_data):
        locations = validated_data.pop('locations')
        user = instance.user
        user.username = validated_data.pop('user')['username']
        user.save(update_fields=['username'])
        obj = super().update(instance, validated_data)
        obj.locations.all().delete()
        for location in locations:
            obj.locations.create(**location)
        return obj


class NestedStudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    date_of_birth = serializers.DateTimeField(source='date_of_birth_datetime')
    gender = serializers.CharField()
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['pk', 'username', 'date_of_birth', 'gender', 'locations']

class TutorSerializer(serializers.ModelSerializer):
    # pk = serializers.HyperlinkedIdentityField(view_name='tutor-detail')
    username = serializers.CharField(source='user.username')
    date_of_birth = serializers.DateTimeField(source='date_of_birth_datetime')
    gender = serializers.CharField()
    hourly_rate = serializers.DecimalField(10, 2)
    available = serializers.BooleanField()
    students = NestedStudentSerializer(many=True, read_only=True)
    locations = LocationSerializer(many=True)
    subjects = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        source='subject_dicts',
    )
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Tutor
        fields = ['pk', 'username', 'date_of_birth', 'gender', 'hourly_rate', 'subjects', 'available', 'students', 'locations', 'rating']

    def create(self, validated_data):
        locations = validated_data.pop('locations')
        user = validated_data['user']
        user.type = User.TUTOR
        user.save(update_fields=['type'])
        obj = super().create(validated_data)
        for location in locations:
            obj.locations.create(**location)
        return obj

    def update(self, instance, validated_data):
        locations = validated_data.pop('locations')
        user = instance.user
        user.username = validated_data.pop('user')['username']
        user.save(update_fields=['username'])
        obj = super().update(instance, validated_data)
        obj.locations.all().delete()
        for location in locations:
            obj.locations.create(**location)
        return obj
