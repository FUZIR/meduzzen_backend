from xml.dom import ValidationErr

from django.db import models

from core.company.models import Company
from core.utils.models import TimeStampedModel


# Create your models here.
class QuizModel(TimeStampedModel):
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=255, blank=False)
    frequency = models.IntegerField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=False, null=True)

    class Meta:
        db_table = "quizzes"

    def clean(self):
        if self.pk and self.questions.count() < 2:
            return ValidationErr("A quiz must have at least 2 questions")
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class QuestionModel(models.Model):
    quiz = models.ForeignKey(QuizModel, on_delete=models.CASCADE, blank=False, related_name="questions")
    question = models.CharField(max_length=255, blank=False)

    class Meta:
        db_table = "questions"

    def clean(self):
        if self.pk and self.answers.count() < 2:
            return ValidationErr("A question must have at least 2 answers")
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class AnswerModel(models.Model):
    question = models.ForeignKey(QuestionModel, on_delete=models.CASCADE, blank=False, related_name="answers")
    answer = models.CharField(max_length=255, blank=False)
    is_correct = models.BooleanField(blank=False)

    class Meta:
        db_table = "answers"