from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'user', views.UserModelViewSet)
urlpatterns = router.urls
