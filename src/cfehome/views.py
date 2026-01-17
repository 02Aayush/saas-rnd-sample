# import pathlib
from django.shortcuts import render
from django.http import HttpResponse

from visits.models import PageVists

# this_dir = pathlib.Path(__file__).resolve().parent


def home_page_view(request, *args, **kwargs):
    qs = PageVists.objects.all() #query into DB using ORM Django.
    page_qs = PageVists.objects.filter(path=request.path)
    my_title = "My Page"
    my_context = {
        "page_title": my_title,
        # "queryset": queryset
        "page_visit_count": page_qs.count(),
        "percent": (page_qs.count() * 100.00) / qs.count(),
        "total_visit_count": qs.count(),
        
    }
    path = request.path
    print("path", path)
    html_template = "home.html"
    PageVists.objects.create(path=request.path)
    return render(request, html_template, my_context)




def my_old_home_page_view(request, *args, **kwargs):
    my_title = "My Page"
    my_context = {
        "page_title": my_title
    }
    html_ = """
    <!DOCTYPE html>
<html>
    <body>
    <h1>{page_title} Hello Template</h1>
    </body>
</html>
    """.format(**my_context)
    # return HttpResponse("<h1>Welcome to the CFE Home Page!<h1>")
    return HttpResponse(html_)