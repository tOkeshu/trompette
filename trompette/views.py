from itertools import chain
import asyncio
import re

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Subquery, Prefetch
from django.utils.timezone import now, timedelta

from .models import Status, Account, Boost, Tag


def pjaxable(fn):
    def _pjaxable(request, *args, **kwargs):
        partial = request.META.get("HTTP_X_PJAX") or kwargs.get("partial")
        kwargs["partial"] = bool(partial)
        return fn(request, *args, **kwargs)

    return _pjaxable


@login_required
def new_status(request):
    if request.method == "GET":
        return render(request, "trompette/new_status.html")
    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    inputs = request.POST
    my_account = request.user.account
    content, in_reply_to_id = inputs["status"], inputs.get("in_reply_to_id")
    status = Status(content=content, account=my_account, in_reply_to_id=in_reply_to_id)
    status.save()

    url = reverse('status', args=(status.id,)) + '#{0}'.format(status.id)
    return HttpResponseRedirect(url)

@pjaxable
def status(request, status_id, partial=False):
    status  = get_object_or_404(Status, pk=status_id)
    thread  = Status.objects.filter(thread=status.thread).all()
    return render(request, "trompette/status.html", {
        "current_status": status,
        "statuses": thread,
        "partial": partial
    })

@login_required
def boost(request, status_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    status = get_object_or_404(Status, pk=status_id)
    boost  = Boost(account=request.user.account, status=status, at=now())
    boost.save()
    return HttpResponseRedirect(reverse('status', args=(status.id,)))

@login_required
def reply(request, status_id):
    status = get_object_or_404(Status, pk=status_id)
    # Only GET requests, if you're looking for the POST request, it is handled by new_status
    if request.method == "GET":
        return render(request, "trompette/reply.html", {"status": status})

@pjaxable
def user_tl(request, username, partial=False):
    account  = Account.objects.get(username=username)
    statuses = set(account.statuses.select_related('account').all())
    boosts   = Boost.objects.select_related('account', 'status') \
                            .filter(account=account).all()       \
                            .prefetch_related('status__account')

    for status in statuses:
        status.boosted_at = None
    for boost in boosts:
        status = boost.status
        status.boosted_from = boost.account
        status.boosted_at   = boost.at
        statuses.add(status)

    statuses = sorted(statuses, key=lambda s: s.boosted_at or s.created_at, reverse=True)

    return render(request, "trompette/timeline.html", {
        "statuses": statuses,
        "partial": partial
    })

def follow(request, username):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    my_account = request.user.account
    target     = get_object_or_404(Account, username)
    my_account.following.add(target)

    url = reverse('account', args=(target.id,))
    return HttpResponseRedirect(url)

