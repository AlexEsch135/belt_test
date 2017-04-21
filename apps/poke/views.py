from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Poke
from django.utils import timezone
from datetime import datetime
from django.db.models import Count


def index(request):
    if 'id' in request.session:
        return redirect('/success')
    return render(request, 'poke/index.html')

def process(request):
    if request.method != 'POST':
        return redirect('/')
    else:
        valid = User.objects.validate(request.POST)
        if valid[0] == True:
            request.session['id'] = valid[1].id
            return redirect('/success')
        else:
            for msg in valid[1]:
                messages.add_message(request, messages.INFO, msg)
            return redirect('/')

def success(request):
    if 'id' not in request.session:
        return redirect('/')
    try:
        user = User.objects.get(id=request.session['id'])
        other_users = User.objects.exclude(id=request.session['id'])
        my_pokes = Poke.objects.filter(poked = user)
        my_pokes_count = other_users.filter(pokerpokes__in=my_pokes).distinct().count()
        users_who_poked_me = other_users.filter(pokerpokes__in=my_pokes).annotate(total_pokes=Count('id')).order_by('-total_pokes')
        other_pokes = other_users.annotate(total_pokes=Count('pokedpokes'))
        context={'users': other_pokes, 'my_pokes_count': my_pokes_count, 'users_who_poked_me': users_who_poked_me, 'user':user}
    except User.DoesNotExist:
        messages.add_message(request, messages.INFO, 'user not found')
        return redirect('/')
    return render(request,'poke/success.html', context)


def poke(request,user_id):
    poker = User.objects.get(id=request.session['id'])
    poked = User.objects.get(id=user_id)
    poke = Poke()
    poke.poker = poker
    poke.poked = poked
    poke.created_at = timezone.now()
    poke.counter+=1
    poke.save()
    return redirect('/success')

def login(request):
    if request.method != "POST":
        return redirect('/')
    else:
        user = User.objects.authenticate(request.POST)
        print user
        if user[0] == True:
            request.session['id'] = user[1].id
            return redirect('/success')
        else:
            messages.add_message(request, messages.INFO, user[1])
            return redirect('/')

def logout(request):
    if 'id' in request.session:
        request.session.pop('id')
    return redirect('/')
