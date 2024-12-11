from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuizViewSet

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet, basename='quiz')

urlpatterns = [
    path("", include(router.urls))
]
