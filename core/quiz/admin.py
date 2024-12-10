from django.contrib import admin

from .models import AnswerModel, QuestionModel, QuizModel


# Register your models here.
@admin.register(QuizModel)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "description", "company", "frequency", "get_questions")
    list_filter = ("id", "title", "company")

    def get_questions(self, obj):
        return "".join([question_data.text for question_data in obj.questions.all()])


admin.site.register([QuestionModel, AnswerModel])
