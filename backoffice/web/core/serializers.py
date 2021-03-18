from rest_framework import serializers

from web.core.models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('file', 'uploaded_at')
