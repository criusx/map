import logging

from django import forms
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie

import git
from server import settings
from server.authentication import ActiveDirectoryBackend


logger = logging.getLogger("helios.view")


@login_required(login_url = '/helios/login/')
def heliosView(request):
    '''
    serve the main helios page
    '''
    try:
        sha1 = git.Repo(search_parent_directories = True).head.object.hexsha
    except Exception as e:
        # TODO not sure what this might throw, catch all for now
        logger.exception(e)
        sha1 = "00000000"

    return render(request, 'helios/viewer.html', {'userName': str(request.user.username),
                                                 'currentHost': request.get_host().split(':')[0],
                                                 'assetPort': settings.NGINX_PORT,
                                                 'asgiServer': request.get_host(),
                                                 'sha1Value': sha1[0:8],
                                                 'sha1Long': sha1,
                                                 })


def loginView(request):
    '''
    serve the login page
    '''
    logout(request)
    username = password = ""
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = ActiveDirectoryBackend().authenticate(username, password)

        if user is not None and user.is_active:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return HttpResponseRedirect(request.POST.get("next", request.GET.get("next", '/helios/')))
    return render(request, 'helios/login.html', {'currentHost': request.get_host().split(':')[0],
                                                'next': request.GET.get("next", request.POST.get("next", '/helios/')),
                                                'assetPort': settings.NGINX_PORT,
                                                })
    # return render_to_response('helios/login.html', {}, RequestContext(request))

