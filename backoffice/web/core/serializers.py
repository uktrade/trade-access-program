from rest_framework import serializers

from web.core.models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'file', 'uploaded_at')
