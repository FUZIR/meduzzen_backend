from django.db import transaction
from django.db.models import Sum, Count, QuerySet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from django.utils.translation import gettext_lazy as _

from core.role.permissions import IsAdminOrOwnerPermission
from .models import QuizModel, ResultsModel, QuizStatus
from .serializers import QuizSerializer, ResultsSerializer


# Create your views here.
class QuizViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action in ["list", "create", "update", "partial_update"]:
            return QuizSerializer
        elif self.action in ["start_quiz", "end_quiz"]:
            return ResultsSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminOrOwnerPermission()]
        else:
            return [IsAuthenticated()]

    def get_queryset(self):
        if self.action == "list":
            company_id = self.request.query_params.get("company")
            if not company_id:
                raise ValidationError({"detail": "Company id is required"})
            return QuizModel.objects.filter(company=company_id).prefetch_related("questions__answers")
        elif self.action in ["start_quiz", "end_quiz"]:
            return QuizModel.objects.filter(id=self.request.data.get("quiz"), company=self.request.data.get("company"))
        return QuizModel.objects.all()

    def calculate_average_score(self, queryset: QuerySet) -> Response:
        total_questions = (
                queryset.values("quiz")
                .annotate(question_count=Count("quiz__questions"))
                .aggregate(total_questions=Sum("question_count"))["total_questions"]
                or 0
        )
        total_correct_answers = (
                queryset.aggregate(total_correct_answers=Sum("correct_answers"))["total_correct_answers"]
                or 0
        )
        if total_questions > 0:
            average_score = (total_correct_answers / total_questions) * 10
        else:
            average_score = 0

        return Response({"average_score": average_score}, status=200)

    @action(methods=["POST"], permission_classes=[IsAuthenticated], detail=False, url_path="start")
    def start_quiz(self, request, *args, **kwargs):
        quiz = get_object_or_404(self.get_queryset().select_related("company"))
        user = request.user
        ResultsModel.objects.create(quiz=quiz, user=user, company=quiz.company)
        return Response({"detail": _("Quiz started successfully")}, status=HTTP_201_CREATED)

    @action(methods=["POST"], permission_classes=[IsAuthenticated], detail=False, url_path="end")
    def end_quiz(self, request, *args, **kwargs):
        quiz = self.get_queryset().select_related("company").first()
        correct_answers = request.data.get("correct_answers")
        if not correct_answers:
            raise ValidationError({"detail": _("Correct answers are required")})
        results = ResultsModel.objects.filter(company=quiz.company, user=request.user,
                                              quiz_status=QuizStatus.STARTED).order_by("-created_at")
        if results.exists():
            result = results.first()
            with transaction.atomic():
                result.quiz_status = QuizStatus.COMPLETED
                result.correct_answers = correct_answers
                result.save()
                return Response({"detail": "Quiz ended successfully"}, status=HTTP_200_OK)

        else:
            return Response({"detail": _("No results found for this user and quiz")}, status=HTTP_404_NOT_FOUND)

    @action(methods=["GET"], permission_classes=[IsAdminOrOwnerPermission], detail=False,
            url_path="company-average-score")
    def get_company_average_score(self, request, *args, **kwargs):
        company_id = self.request.query_params.get("company")
        results = ResultsModel.objects.filter(company=company_id).select_related("quiz").prefetch_related(
            "quiz__questions")
        if not results:
            return Response({"detail": _("Quiz data not found")}, status=HTTP_404_NOT_FOUND)
        return self.calculate_average_score(results)

    @action(methods=["GET"], permission_classes=[IsAuthenticated], detail=False, url_path="average-score")
    def get_average_score(self, request, *args, **kwargs):
        users_results = ResultsModel.objects.all().select_related("quiz").prefetch_related("quiz__questions")
        if not users_results:
            return Response({"detail": _("Users results not found")}, status=HTTP_404_NOT_FOUND)
        return self.calculate_average_score(users_results)
