# import pathlib
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from django.http import HttpResponse

from visits.models import PageVists

LOGIN_URL = settings.LOGIN_URL

# this_dir = pathlib.Path(__file__).resolve().parent


def home_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        print(request.user.first_name)
    return about_view(request, *args, **kwargs)


def about_view(request, *args, **kwargs):
    qs = PageVists.objects.all() #query into DB using ORM Django.
    page_qs = PageVists.objects.filter(path=request.path)
    
    try:
        percent = (page_qs.count() * 100.00) / qs.count()
    except ZeroDivisionError:
        percent = 0.00
        
    my_title = "My Page"
    my_context = {
        "page_title": my_title,
        # "queryset": queryset
        "page_visit_count": page_qs.count(),
        "percent": percent,
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

valid_code = "sv123"

def pw_protected_view(request, * args, **kwargs):
    is_allowed = request.session.get("protected_page_allowed") or 0
    if request.method == "POST":
        user_pw_sent = request.POST.get("code") or None
        if user_pw_sent == valid_code:
            request.session["protected_page_allowed"] = is_allowed
    if is_allowed:
        return render(request, "protected/view.html", {})
        
    return render(request, "protected/entry.html", {})

@login_required(login_url=LOGIN_URL)
def user_only_view(request, * args, **kwargs):
    print(request.user.is_staff)
    return render(request, "protected/user-only.html", {})

@staff_member_required(login_url=LOGIN_URL)
def staff_only_view(request, * args, **kwargs):
    return render(request, "protected/user-only.html", {})
