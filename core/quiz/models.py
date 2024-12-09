from django.db import models
from django.db.models import TextChoices
from rest_framework.exceptions import ValidationError

from core.company.models import Company
from core.utils.models import TimeStampedModel
from core.user.models import CustomUser
from django.utils.translation import gettext_lazy as _


# Create your models here.
class QuizModel(TimeStampedModel):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=255, blank=False)
    frequency = models.IntegerField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=False, null=True, related_name="quizzes")

    class Meta:
        db_table = "quizzes"

    def clean(self):
        if self.pk and self.questions.count() < 2:
            return ValidationError({"detail":_("A quiz must have at least 2 questions")})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class QuestionModel(TimeStampedModel):
    quiz = models.ForeignKey(QuizModel, on_delete=models.CASCADE, blank=False, related_name="questions")
    text = models.CharField(max_length=255, blank=False)

    class Meta:
        db_table = "questions"

    def clean(self):
        if self.pk and self.answers.count() < 2:
            return ValidationError({"detail":_("A question must have at least 2 answers")})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class AnswerModel(TimeStampedModel):
    question = models.ForeignKey(QuestionModel, on_delete=models.CASCADE, blank=False, related_name="answers")
    text = models.CharField(max_length=255, blank=False)
    is_correct = models.BooleanField(blank=False)

    class Meta:
        db_table = "answers"


class QuizStatus(TextChoices):
    STARTED = "ST", "Started"
    COMPLETED = "CM", "Completed"


class ResultsModel(TimeStampedModel):
    quiz = models.ForeignKey(QuizModel, on_delete=models.CASCADE, blank=False, related_name="quiz")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False, related_name="user")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=False, null=True, related_name="company")
    score = models.FloatField(default=0.0)
    quiz_status = models.CharField(choices=QuizStatus.choices, default=QuizStatus.STARTED, blank=False, max_length=2)
    correct_answers = models.IntegerField(null=True, blank=False)

    class Meta:
        db_table = "results"

    def clean(self):
        if self.pk and self.quiz.questions.count() < self.correct_answers:
            raise ValidationError({"detail": _("Correct answers count can't be more than questions count")})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
