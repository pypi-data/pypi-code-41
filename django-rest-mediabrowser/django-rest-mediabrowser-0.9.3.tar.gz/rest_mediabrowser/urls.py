from django.urls import path, include, re_path
from .views import *
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter, SimpleRouter

router = DefaultRouter()
router.register(r'collections', CollectionViewSet)
router.register(r'collections', SharedCollectionViewSet,
                basename='shared-collection')
router.register(r'images', MediaImageViewSet)
router.register(r'files', MediaFileViewSet)
router.register(r'shared/images', SharedMediaImageViewSet,
                basename='shared-images')
router.register(r'shared/files', SharedMediaFileViewSet,
                basename='shared-file')


urlpatterns = [
    path('', include(router.urls)),
    #     re_path(r'^(?P<path>.*)$', MediaFilesView.as_view(),
    #             name='serve_private_file'),
    path('images/<int:pk>/file.<str:ext>',
         MediaStorageImageView.as_view(), name='mb-image'),
    path('images/<int:pk>/thumbnail.<str:ext>',
         MediaStorageImageThumbnailView.as_view(), name='mb-thumbnail'),
    path('files/<int:pk>/file.<str:ext>',
         MediaStorageFileView.as_view(), name='mb-file'),
]
