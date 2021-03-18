from django.urls import path

from web.core.apis import ImageUploadAPIView

app_name = 'core'
urlpatterns = [
    path(
        'image-upload/',
        ImageUploadAPIView.as_view(),
        name='image-upload'
    )
]
