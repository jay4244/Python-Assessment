from rest_framework import serializers
from .models import Course, Student

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Course.objects.all()
    )

    class Meta:
        model = Student
        fields = '__all__'
        
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['courses'] = CourseSerializer(instance.courses.all(), many=True).data
        return response
