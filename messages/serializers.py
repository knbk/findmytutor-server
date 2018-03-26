from rest_framework import serializers

from .models import Message, MessageThread


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['pk', 'content', 'sent_at', 'sent_by']


class MessageThreadSerializer(serializers.ModelSerializer):
    content = serializers.CharField(write_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = MessageThread
        fields = ['content', 'student', 'tutor', 'messages']
        read_only_fields = ['student', 'tutor']
