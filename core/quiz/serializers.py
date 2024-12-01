from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import QuizModel, QuestionModel, AnswerModel
from django.utils.translation import gettext_lazy as _


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerModel
        fields = [
            "answer",
            "is_correct"
        ]
        extra_kwargs = {
            "question": {"read_only": True}
        }


class GetAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerModel
        fields = [
            "id",
            "answer",
            "is_correct"
        ]
        extra_kwargs = {
            "question": {"read_only": True}
        }


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = QuestionModel
        fields = [
            "question",
            "answers"
        ]

    def validate_answers(self, answers):
        correct_answers = [answers for answer in answers if answer["is_correct"]]
        if len(correct_answers) != 1:
            return ValidationError(_("There must be only one correct answer."))
        return answers


class GetQuestionSerializer(serializers.ModelSerializer):
    answers = GetAnswerSerializer(many=True)

    class Meta:
        model = QuestionModel
        fields = [
            "id",
            "question",
            "answers"
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = QuizModel
        fields = [
            "title",
            "description",
            "frequency",
            "questions",
            "company"
        ]

    def create(self, validated_data):
        questions = validated_data.pop("questions", [])

        quiz = QuizModel.objects.create(**validated_data)

        for question in questions:
            answers = question.pop("answers", [])
            quest = QuestionModel.objects.create(quiz=quiz, **question)
            for answer in answers:
                AnswerModel.objects.create(question=quest, **answer)

        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", [])

        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.frequency = validated_data.get("frequency", instance.frequency)
        instance.save()

        existing_questions = {question.id: question for question in instance.questions.all()}

        for question_data in questions_data:
            question_id = question_data.get("id")
            if question_id and question_id in existing_questions:
                question = existing_questions.pop(question_id)
                question.question = question_data.get("question", question.question)
                question.save()

                existing_answers = {answer.id: answer for answer in instance.answers}

                for answer_data in question_data.get("answers", []):
                    answer_id = answer_data.get("id")
                    if answer_id and answer_id in existing_answers:
                        answer = existing_answers.pop(answer_id)
                        answer.answer = answer_data.get("answer", answer.answer)
                        answer.is_correct = answer_data.get("is_correct", answer.is_correct)
                        answer.save()
                    else:
                        AnswerModel.objects.create(question=question, **answer_data)

                for answer in existing_answers.values():
                    answer.delete()
            else:
                answers_data = question_data.pop("answers", [])
                new_question = QuestionModel.objects.create(quiz=instance, **question_data)
                for answer_data in answers_data:
                    AnswerModel.objects.create(question=new_question, **answer_data)
        for question in existing_questions.values():
            question.delete()

        return instance

    def validate(self, data):
        questions = data.get("questions", [])
        if len(questions) < 2:
            raise serializers.ValidationError(_("A quiz must have at least 2 questions."))

        for question in questions:
            answers = question.get("answers", [])
            if len(answers) < 2:
                raise serializers.ValidationError(_("Each question must have at least 2 answer options."))

        return data


class GetQuizSerializer(serializers.ModelSerializer):
    questions = GetQuestionSerializer(many=True)

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
