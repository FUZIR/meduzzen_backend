import smtplib
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db.models import F, ExpressionWrapper, DurationField
from django.utils.timezone import now

from core.quiz.models import ResultsModel, QuizStatus


def get_users_with_available_quizzes():
    results = ResultsModel.objects.filter(quiz_status=QuizStatus.COMPLETED).select_related("quiz", "user")
    queryset = results.annotate(
        days_since_update=ExpressionWrapper((now() - F("updated_at")), output_field=DurationField()),
        required_duration=ExpressionWrapper(F("quiz__frequency") * timedelta(days=1), output_field=DurationField()),
        user_email=F("user__email"),
        quiz_title=F("quiz__title"),
    )
    return queryset.filter(days_since_update__gt=F("required_duration"))


@shared_task()
def send_email_with_notification():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    users = get_users_with_available_quizzes()
    for user in users:
        subject = "Quiz Notification"
        body = (
            f"Dear {user.user_email},\n\n"
            f"The quiz '{user.quiz_title}' is now available for you to complete! "
            f"Log in to the system to start the quiz."
        )
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(settings.EMAIL_HOST_USER, user.user_email, message)
    server.quit()
