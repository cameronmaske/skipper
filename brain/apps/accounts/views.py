from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm


def register_or_login(request):
    if User.objects.all().exists():
        return redirect(reverse("login"))
    else:
        return redirect(reverse("register"))


def register(request):
    if User.objects.all().exists():
        return redirect(reverse("login"))
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")
    return render(request, "accounts/register.html", {"form": form})
