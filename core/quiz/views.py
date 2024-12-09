from django.db import transaction
from django.db.models import Count, QuerySet, F, FloatField, Avg, OuterRef, Subquery
from django.db.models.functions import TruncDate
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from django.utils.translation import gettext_lazy as _

from core.role.permissions import IsAdminOrOwnerPermission
from core.utils.csv_writer import return_csv
from user.models import CustomUser
from .models import QuizModel, ResultsModel, QuizStatus
from .serializers import QuizSerializer, ResultsSerializer, RatingListSerializer, CompanyQuizzesHistory, \
    QuizzesAveragesSerializer, UsersAverageSerializer, CompanyUsersWithLastTestSerializer


# Create your views here.
class QuizViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "create", "update", "partial_update"]:
            return QuizSerializer
        elif self.action in ["start_quiz", "end_quiz"]:
            return ResultsSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminOrOwnerPermission()]
        return super().get_permissions()

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
        total_average_score = (
                queryset.aggregate(average_score=Avg("score"))["average_score"] or 0
        )

        return Response({"average_score": total_average_score}, status=200)

    @action(methods=["POST"], permission_classes=[IsAuthenticated], detail=False, url_path="start")
    def start_quiz(self, request, *args, **kwargs):
        quiz = get_object_or_404(self.get_queryset().select_related("company"))
        user = request.user
        ResultsModel.objects.create(quiz=quiz, user=user, company=quiz.company)
        return Response({"detail": _("Quiz started successfully")}, status=HTTP_201_CREATED)

    @action(methods=["POST"], permission_classes=[IsAuthenticated], detail=False, url_path="end")
    def end_quiz(self, request, *args, **kwargs):
        quiz = get_object_or_404(self.get_queryset().select_related("company"))
        correct_answers = request.data.get("correct_answers")
        if correct_answers is None:
            raise ValidationError({"detail": _("Correct answers are required")})
        results = (ResultsModel.objects.filter(company=quiz.company, user=request.user,
                                               quiz_status=QuizStatus.STARTED).select_related("quiz").prefetch_related(
            "quiz__questions").annotate(questions_count=Count("quiz__questions")).order_by("-created_at"))
        if results.exists():
            result = results.first()
            with transaction.atomic():
                result.quiz_status = QuizStatus.COMPLETED
                result.correct_answers = correct_answers
                result.score = float(
                    (correct_answers / result.questions_count) * 10 if result.questions_count > 0 else 0.0)
                result.save()
                return Response({"detail": "Quiz ended successfully"}, status=HTTP_200_OK)

        else:
            return Response({"detail": _("No results found for this user and quiz")}, status=HTTP_404_NOT_FOUND)

    @action(methods=["GET"], permission_classes=[IsAdminOrOwnerPermission], detail=False,
            url_path="company-average-score")
    def get_company_average_score(self, request, *args, **kwargs):
        company_id = request.query_params.get("company")
        results = ResultsModel.objects.filter(company=company_id)
        if not results:
            return Response({"detail": _("Quiz data not found")}, status=HTTP_404_NOT_FOUND)
        return self.calculate_average_score(results)

    @action(methods=["GET"], permission_classes=[IsAuthenticated], detail=False, url_path="average-score")
    def get_average_score(self, request, *args, **kwargs):
        users_results = ResultsModel.objects.all()
        if not users_results:
            return Response({"detail": _("Users results not found")}, status=HTTP_404_NOT_FOUND)
        return self.calculate_average_score(users_results)

    @action(methods=["GET"], permission_classes=[IsAuthenticated], detail=False, url_path="statistic-csv")
    def get_user_results(self, request, *args, **kwargs):
        user_results = (ResultsModel.objects.filter(user=request.user).select_related("company"))
        return return_csv(user_results)

    @action(methods=["GET"], permission_classes=[IsAdminOrOwnerPermission], detail=False, url_path="statistic-csv-by-id")
    def get_user_results_by_id(self, request, *args, **kwargs):
        user_id = request.query_params.get("user")
        company_id = request.query_params.get("company")
        if not user_id or not company_id:
            return Response({"detail": _("User and company ids are required")})
        user_in_company = CustomUser.objects.filter(id=user_id, company_id=company_id).exists()
        if not user_in_company:
            return Response({"detail": _("The user does not belong to this company")}, status=HTTP_404_NOT_FOUND)

        user_results = (ResultsModel.objects.filter(user=user_id, company=company_id).select_related("company"))
        return return_csv(user_results)

    @action(methods=["GET"], permission_classes=[IsAdminOrOwnerPermission], detail=False,
            url_path="company-results-csv")
    def get_company_results(self, request, *args, **kwargs):
        company_id = request.query_params.get("company")
        if not company_id:
            return Response({"detail": "Company ID is required"}, status=HTTP_400_BAD_REQUEST)

        user_id = request.query_params.get("user")
        results = ResultsModel.objects.filter(company=company_id)
        if user_id:
            results = results.filter(user=user_id)
        return return_csv(results)

    @action(methods=["GET"], permission_classes=[IsAuthenticated], detail=False, url_path="get-ratings")
    def get_ratings(self, request, *args, **kwargs):
        queryset = ResultsModel.objects.filter(quiz_status=QuizStatus.COMPLETED).select_related("user",
                                                                                                "user__company").values(
            "user",
            "user_id", "user__username", "user__first_name", "user__last_name", "user__company").annotate(
            average_score=Avg("score")).order_by("-average_score")
        if not queryset.exists():
            return Response({"detail": _("Ratings not found")}, status=HTTP_404_NOT_FOUND)
        serializer = RatingListSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=["GET"], permission_classes=[IsAdminOrOwnerPermission], detail=False, url_path="quizzes-history")
    def company_quizzes_history(self, request, *args, **kwargs):
        company_id = request.query_params.get("company")
        queryset = (
            ResultsModel.objects.filter(company=company_id, quiz_status=QuizStatus.COMPLETED).select_related("user")
            .annotate(last_test_time=F("updated_at")).order_by("-last_test_time"))
        if not queryset.exists():
            return Response({"detail": _("Quizzes history not found")}, status=HTTP_404_NOT_FOUND)
        serializer = CompanyQuizzesHistory(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=["GET"], permission_classes=[IsAuthenticated], detail=False, url_path="quizzes-average")
    def get_quizzes_average(self, request, *args, **kwargs):
        queryset = ResultsModel.objects.filter(quiz_status=QuizStatus.COMPLETED).prefetch_related("quiz")

        quizzes_average = (
            queryset
            .annotate(date=TruncDate("updated_at"))
            .values("quiz__id", "quiz__title", "date")
            .annotate(
                quiz_id=F("quiz__id"),
                quiz_title=F("quiz__title")
            )
            .annotate(average_score=Avg("score", output_field=FloatField()))
            .order_by("quiz__id", "-date")
        )
        if not quizzes_average.exists():
            return Response({"detail": _("Quizzes average not found")}, status=HTTP_404_NOT_FOUND)

        serializer = QuizzesAveragesSerializer(quizzes_average, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=["GET"], permission_classes=[IsAuthenticated], detail=False, url_path="users-average")
    def get_users_average(self, request, *args, **kwargs):
        queryset = ResultsModel.objects.filter(quiz_status=QuizStatus.COMPLETED)

        users_average = (
            queryset
            .annotate(date=TruncDate("updated_at"))
            .values("date")
            .annotate(average_score=Avg("score", output_field=FloatField()))
            .order_by("-date")
        )
        if not users_average.exists():
            return Response({"detail": _("Users averages scores not found")}, status=HTTP_404_NOT_FOUND)
        serializer = UsersAverageSerializer(users_average, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=["GET"], permission_classes=[IsAuthenticated], detail=False, url_path="user-average-by-id")
    def get_user_average_by_id(self, request, *args, **kwargs):
        user_id = request.query_params.get("user")
        queryset = ResultsModel.objects.filter(quiz_status=QuizStatus.COMPLETED, user=user_id)

        user_averages = (
            queryset
            .annotate(date=TruncDate("updated_at"))
            .values("date")
            .annotate(average_score=Avg("score", output_field=FloatField()))
            .order_by("-date")
        )
        if not user_averages.exists():
            return Response({"detail": _("User averages by id not found")}, status=HTTP_404_NOT_FOUND)
        serializer = UsersAverageSerializer(user_averages, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=["GET"], permission_classes=[IsAdminOrOwnerPermission], detail=False,
            url_path="company-users-with-last-test")
    def get_company_users_with_last_test(self, request, *args, **kwargs):
        company_id = request.query_params.get("company")
        if not company_id:
            return Response({"detail": _("Company id is required")}, status=HTTP_400_BAD_REQUEST)
        results = ResultsModel.objects.filter(user_id=OuterRef("user_id"), company=company_id).order_by("-updated_at")

        results_with_last_test_time = ResultsModel.objects.filter(
            id=Subquery(results.values("id")[:1])
        ).select_related("quiz", "user").annotate(last_time_taken=F("updated_at"))
        if not results_with_last_test_time.exists():
            return Response({"detail": _("Company user with last taken time not found")}, status=HTTP_404_NOT_FOUND)

        serializer = CompanyUsersWithLastTestSerializer(results_with_last_test_time, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
