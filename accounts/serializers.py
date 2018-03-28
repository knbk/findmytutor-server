from rest_framework import serializers

from .models import User, Student, Tutor, Profile, Location


class UserSerializer(serializers.ModelSerializer):
    pk = serializers.HyperlinkedIdentityField(view_name='user-detail')
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
        fields = ['pk', 'city', 'street_address', 'zip_code', 'latitude', 'longitude']


class StudentSerializer(serializers.ModelSerializer):
    pk = serializers.HyperlinkedIdentityField(view_name='student-detail')
    username = serializers.CharField(source='user.username')
    date_of_birth = serializers.DateField()
    gender = serializers.CharField()
    tutors = serializers.StringRelatedField(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['pk', 'username', 'date_of_birth', 'gender', 'tutors', 'locations']

    def create(self, validated_data):
        user = validated_data['user']
        user.type = User.STUDENT
        user.save(update_fields=['type'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = instance.user
        user.username = validated_data.pop('user')['username']
        user.save(update_fields=['username'])
        return super().update(instance, validated_data)


class TutorSerializer(serializers.ModelSerializer):
    # pk = serializers.HyperlinkedIdentityField(view_name='tutor-detail')
    username = serializers.CharField(source='user.username')
    date_of_birth = serializers.DateField()
    gender = serializers.CharField()
    hourly_rate = serializers.DecimalField(10, 2)
    available = serializers.BooleanField()
    students = serializers.StringRelatedField(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Tutor
        fields = ['pk', 'username', 'date_of_birth', 'gender', 'hourly_rate', 'subjects', 'level', 'available', 'students', 'locations']

    def create(self, validated_data):
        user = validated_data['user']
        user.type = User.TUTOR
        user.save(update_fields=['type'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = instance.user
        user.username = validated_data.pop('user')['username']
        user.save(update_fields=['username'])
        return super().update(instance, validated_data)
