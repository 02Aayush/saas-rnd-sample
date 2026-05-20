import helpers.numbers
from django.shortcuts import render

from visits.models import PageVisits
# Create your views here.
def landing_page_view(request):
    qs = PageVisits.objects.all()
    PageVisits.objects.create(path=request.path)
    page_views_formatted = helpers.numbers.shorten_number(qs.count() * 100_000)
    social_views_formatted = helpers.numbers.shorten_number(qs.count() * 23_000)
    return render(request, "landing/main.html", {
        "page_visit_count": page_views_formatted,
        "social_visit_count": social_views_formatted
    })