from django.contrib import admin

from .models import QuizModel, AnswerModel, QuestionModel


# Register your models here.
@admin.register(QuizModel)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "description", "company", "frequency", "get_questions")
    list_filter = ("id", "title", "company")

    def get_questions(self, obj):
        return "".join([question.question for question in obj.questions.all()])


admin.site.register([QuestionModel, AnswerModel])
