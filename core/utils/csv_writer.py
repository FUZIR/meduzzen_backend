import csv

from django.db.models import QuerySet
from django.http import HttpResponse


def return_csv(results: QuerySet) -> HttpResponse:
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_results.csv"'
    writer = csv.writer(response)
    writer.writerow(["id", "quiz_name", "company", "correct_answers", "score", "started_at", "ended_at"])
    for result in results:
        writer.writerow([result.id,
                         result.quiz.title,
                         result.quiz.company,
                         result.correct_answers,
                         round(result.score or 0, 2),
                         result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                         result.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                         ])
    return response