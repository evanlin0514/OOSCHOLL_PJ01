from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
from .forms import SignupForm, LoginForm
from .models import User, List, Stock, DataManager
import json


# Create your views here.

@login_required
def index(request):
    user = request.user
    watchlists = List.objects.filter(user=user)
    all_stocks = Stock.objects.all()
    
    watchlist_data = []
    for watchlist in watchlists:
        stocks = Stock.objects.filter(data_managers__list=watchlist)
        watchlist_data.append({
            'watchlist': watchlist,
            'stocks': stocks
        })

    context = {
        'watchlists': watchlists,
        'watchlist_data': watchlist_data,
        'all_stocks': all_stocks,
    }
    return render(request, 'index.html', context)

# signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)    
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
@require_POST
def create_watchlist(request):
    name = request.POST.get('watchlist_name')
    if name:
        try:
            watchlist = List.objects.create(user=request.user, name=name)
            return JsonResponse({
                'success': True,
                'watchlist': {
                    'id': watchlist.id,
                    'name': watchlist.name
                }
            })
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'A watchlist with this name already exists'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid watchlist name'}, status=400)

@login_required
@require_POST
def remove_watchlist(request, watchlist_id):
    try:
        watchlist = get_object_or_404(List, id=watchlist_id, user=request.user)
        watchlist_name = watchlist.name
        watchlist.delete()
        return JsonResponse({'success': True, 'message': f'Watchlist "{watchlist_name}" has been removed.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def add_to_watchlist(request, stock_id):
    try:
        stock = get_object_or_404(Stock, id=stock_id)
        watchlist_id = request.POST.get('watchlist_id')
        
        if not watchlist_id:
            return JsonResponse({'success': False, 'message': 'Watchlist ID is required'}, status=400)
        
        watchlist = get_object_or_404(List, id=watchlist_id, user=request.user)
        
        if not DataManager.objects.filter(list=watchlist, stock=stock).exists():
            DataManager.objects.create(list=watchlist, stock=stock)
            return JsonResponse({
                'success': True, 
                'message': f'{stock.ticker} added to {watchlist.name}',
                'stock': {
                    'id': stock.id,
                    'ticker': stock.ticker,
                    'close': str(stock.close),
                    'd5': str(stock.d5) if stock.d5 is not None else None,
                    'd10': str(stock.d10) if stock.d10 is not None else None,
                    'd15': str(stock.d15) if stock.d15 is not None else None    
                },
                'watchlist': {
                    'id': watchlist.id,
                    'name': watchlist.name
                }
            })
        else:
            return JsonResponse({'success': False, 'message': f'{stock.ticker} is already in {watchlist.name}'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_POST
def remove_from_watchlist(request, watchlist_id, stock_id):
    try:
        stock = get_object_or_404(Stock, id=stock_id)
        watchlist = get_object_or_404(List, id=watchlist_id, user=request.user)
        DataManager.objects.filter(list=watchlist, stock=stock).delete()
        return JsonResponse({
            'success': True, 
            'stock_id': stock_id,
            'stock_ticker': stock.ticker,
            'watchlist_id': watchlist_id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@transaction.atomic
def delete_user_and_lists(user_id):
    user = User.objects.get(id=user_id)
    user.delete()  # This will also delete all associated lists due to CASCADE