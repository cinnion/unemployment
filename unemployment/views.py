from django.shortcuts import render, redirect, get_object_or_404


def homepage(request):
    return render(request, "master.html")
