from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def register(request):
    if request.method == 'GET':
        form = UserCreationForm()
        context = {'form': form}
        return render(request, 'registration/register.html', context)
    elif request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            created_user = form.save()
            login(request, created_user)
            return redirect('learning_logs:index')
        else:
            # Render error form
            context = {'form': form}
            return render(request, 'registration/register.html', context)
    else:
        raise Exception("Undefined HTTP request method.")
