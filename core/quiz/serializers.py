from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.company.serializers import CompanyListSerializer
from core.user.serializers import UserListSerializer
from .models import QuizModel, QuestionModel, AnswerModel, ResultsModel
from django.utils.translation import gettext_lazy as _


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerModel
        fields = [
            "id",
            "text",
            "is_correct"
        ]
        extra_kwargs = {
            "question": {"read_only": True},
            "id": {"read_only": True}
        }


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = QuestionModel
        fields = [
            "id",
            "text",
            "answers"
        ]
        extra_kwargs = {
            "id": {"read_only": True}
        }

    def validate_answers(self, answers):
        correct_answers = [answer for answer in answers if answer["is_correct"]]
        if len(correct_answers) != 1:
            return ValidationError(_("There must be only one correct answer."))
        return answers


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = QuizModel
        fields = [
            "id",
            "title",
            "description",
            "frequency",
            "questions",
            "company"
        ]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])

        quiz = QuizModel.objects.create(**validated_data)
        question_models = []
        answer_models = []
        for question in questions_data:
            answers_data = question.pop("answers", [])
            quest = QuestionModel(quiz=quiz, **question)
            question_models.append(quest)
            answer_models.extend(AnswerModel(question=quest, **answer) for answer in answers_data)

        with transaction.atomic():
            QuestionModel.objects.bulk_create(question_models)
            AnswerModel.objects.bulk_create(answer_models)
        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", [])

        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.frequency = validated_data.get("frequency", instance.frequency)
        instance.save()

        existing_questions = {question.id: question for question in instance.questions.all()}

        questions_for_update = []
        answers_for_update = []

        questions_for_create = []
        answers_for_create = []
        for question_data in questions_data:
            question_id = question_data.get("id")
            if question_id and question_id in existing_questions:
                question = existing_questions.pop(question_id)
                question.text = question_data.get("text", question.text)
                questions_for_update.append(question)

                existing_answers = {answer.id: answer for answer in instance.answers.all()}

                for answer_data in question_data.get("answers", []):
                    answer_id = answer_data.get("id")
                    if answer_id and answer_id in existing_answers:
                        answer = existing_answers.pop(answer_id)
                        answer.text = answer_data.get("text", answer.text)
                        answer.is_correct = answer_data.get("is_correct", answer.is_correct)
                        answers_for_update.append(answer)
                    else:
                        answers_for_create.append(AnswerModel(question=question, **answer_data))

                AnswerModel.objects.filter(id__in=existing_answers.keys()).delete()
            else:
                answers_data = question_data.pop("answers", [])
                new_question = QuestionModel(quiz=instance, **question_data)
                questions_for_create.append(new_question)
                for answer_data in answers_data:
                    answers_for_create.append(AnswerModel(question=new_question, **answer_data))

        QuestionModel.objects.filter(id__in=existing_questions.keys()).delete()

        with transaction.atomic():
            if questions_for_create:
                QuestionModel.objects.bulk_create(questions_for_create)
            if answers_for_create:
                AnswerModel.objects.bulk_create(answers_for_create)
            if questions_for_update:
                QuestionModel.objects.bulk_update(questions_for_update, ["text"])
            if answers_for_update:
                AnswerModel.objects.bulk_update(answers_for_update, ["text", "is_correct"])
        return instance

    def validate(self, data):
        questions = data.get("questions", [])
        if len(questions) < 2:
            raise ValidationError({"detail": _("A quiz must have at least 2 questions.")})

        for question in questions:
            answers = question.get("answers", [])
            if len(answers) < 2:
                raise ValidationError({"detail": _("Each question must have at least 2 answer options.")})

        return data


class ResultsSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer()
    user = UserListSerializer()
    company = CompanyListSerializer()

    class Meta:
        model = ResultsModel
        fields = [
            "id",
            "quiz",
            "user",
            "company",
            "correct_answers",
        ]
        extra_kwargs = {
            "id": {"read_only": True}
        }


class RatingListSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    average_score = serializers.FloatField()

    class Meta:
        model = ResultsModel
        fields = [
            "user",
            "average_score"
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'id': instance['user_id'],
            'username': instance['user__username'],
            'first_name': instance['user__first_name'],
            'last_name': instance['user__last_name'],
            'company': instance.get('user__company__name', None)
        }
        return representation

class CompanyQuizzesHistory(serializers.ModelSerializer):
    user = UserListSerializer()
    score = serializers.FloatField()
    last_test_time = serializers.DateTimeField()

    class Meta:
        model = ResultsModel
        fields = [
            "id",
            "user",
            "quiz_id",
            "score",
            "last_test_time"
        ]

class QuizzesAveragesSerializer(serializers.ModelSerializer):
    quiz_id = serializers.IntegerField()
    quiz_title = serializers.CharField()
    average_score = serializers.FloatField()
    date = serializers.DateField()

    class Meta:
        model = ResultsModel
        fields = [
            "quiz_id",
            "quiz_title",
            "average_score",
            "date",
        ]

class UsersAverageSerializer(serializers.ModelSerializer):
    average_score = serializers.FloatField()
    date = serializers.DateField()

    class Meta:
        model=ResultsModel
        fields = [
            "average_score",
            "date"
        ]

class CompanyUsersWithLastTestSerializer(serializers.ModelSerializer):
    last_time_taken = serializers.DateTimeField()

    class Meta:
        model = ResultsModel
        fields = [
            "quiz_id",
            "user",
            "score",
            "last_time_taken",
        ]