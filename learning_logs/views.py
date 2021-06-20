from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here.

def index(request):
    """ Learning logs Django web application home page. """
    # Responds to the request with the web page template
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    """ Queries data from Topic object/database and puts them into list template. """
    # All created Topic objects (from database)
    topics = Topic.objects.filter(user=request.user).order_by('date_added')
    # Data format for template
    context = {'topics': topics}
    # Put data into template and sent template back
    return render(request, 'learning_logs/topics.html', context)

def check_user(user, user2):
    if user != user2:
        raise Http404

@login_required
def topic(request, topic_id):
    """ Queries and returns a specified topic web page by topic_id. """
    # Get the specified Topic object (db query)
    topic = Topic.objects.get(id=topic_id)

    check_user(topic.user, request.user)

    # Order by date_added (descending) (db query)
    entries = topic.entry_set.order_by('-date_added')
    # Data to put into the template
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """ Renders a web page where you can add/create new topic. """
    if request.method == 'GET':
        # Render form first time
        form = TopicForm()
        template_context = {'form': form}
        return render(request, 'learning_logs/new_topic.html', template_context)
    elif request.method == 'POST':
        form = TopicForm(data=request.POST)
        if form.is_valid():
            # Redirect user to the topics list page
            created_topic = form.save(commit=False)
            created_topic.user = request.user
            created_topic.save()
            return redirect('learning_logs:topics')
        else:
            # Render invalid form to help user
            template_context = {'form': form}
            return render(request, 'learning_logs/new_topic.html', template_context)
    else:
        raise Exception("Web page doesn't support other HTTP request methods.")

@login_required
def new_entry(http_request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    check_user(topic.user, http_request.user)

    if http_request.method == 'GET':
        form = EntryForm()
        template_render_context = {'form': form, 'topic': topic}
        return render(http_request, 'learning_logs/new_entry.html', template_render_context)
    elif http_request.method == 'POST':
        form = EntryForm(data=http_request.POST)
        if form.is_valid():
            # Saving form data to the model/database
            # save form + specify the parent topic
            created_entry = form.save(commit=False) # save form/create Entry model/object without commit to database
            created_entry.topic = topic
            created_entry.save() # finally commit to the database
            # Redirect to the selected topic
            return redirect('learning_logs:topic', topic_id=topic_id)
        else:
            template_render_context = {'form': form, 'topic': topic}
            return render(http_request, 'learning_logs/new_entry.html', template_render_context)
    else:
        raise Exception("Web page doesn't support other HTTP request methods.")

@login_required
def edit_entry(http_request, entry_id):
    """ Edits entry with the id entry_id created previously, access via topics/. """
    # Get topic from all possible entries
    entry = Entry.objects.get(id=entry_id)
    # Entry parent
    topic = entry.topic

    if topic.user != http_request.user:
        raise Http404

    if http_request.method == 'GET':
        form = EntryForm(instance=entry)
        template_render_context = {'form': form, 'topic': topic, 'entry': entry}
        return render(http_request, 'learning_logs/edit_entry.html', template_render_context)
    elif http_request.method == 'POST':
        # Edit instance entry with data from request
        form = EntryForm(instance=entry, data=http_request.POST)
        if form.is_valid():
            # Save edited (data) entry (instance)
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
        else:
            template_render_context = {'form': form, 'topic': topic, 'entry': entry}
            return render(http_request, 'learning_logs/edit_entry.html', template_render_context)
    else:
        raise Exception("Web page doesn't support other HTTP request methods.")
