from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here.

def index(request):
	"""Домашняя страница приложения Learning Log."""
	return render(request, 'learning_logs/index.html')

def more_inf(request):
	return render(request,'learning_logs/more_inf.html')

def topics(request):
	"""Выводит список тем."""
	public_topics = Topic.objects.filter(public=True).order_by('date_added')
	if request.user.is_authenticated:
		private_topics = Topic.objects.filter(owner=request.user).order_by('date_added')
		topics = public_topics | private_topics
	else:
		topics = public_topics
	
	context = {'topics': topics}
	return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
	"""Выводит одну тему и все её записи."""
	topic = get_object_or_404(Topic, id=topic_id)
	#Проверка того, что тема принадлежит текущему пользователю
	check_topic_owner(topic.owner, request)

	entries = topic.entry_set.order_by('-date_added')
	context = {'topic': topic, 'entries': entries}
	return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
	"""Определяет новую тему"""
	if request.method != 'POST':
		#Данные не отправлялись;создаётся пустая форма.
		form = TopicForm()
	else:
		#отправлены данные POST; обработать данные.
		form = TopicForm(data=request.POST)
		if form.is_valid():
			new_topic = form.save(commit=False)
			new_topic.owner = request.user
			new_topic.save()
			return redirect('learning_logs:topics')

	#Вывести пустую или недействительную форму.
	context = {'form': form}
	return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
	"""Добавляет новую запись по конкретной теме"""
	topic = get_object_or_404(Topic, id=topic_id)
	check_topic_owner(topic.owner, request)
	if request.method != 'POST':
		#Данные не отправлялись; создаётся пустая форма.
		form = EntryForm()
	else:
		#Отправленные данные POST; обработать данные.
		form = EntryForm(data=request.POST)
		if form.is_valid():
			new_entry = form.save(commit=False)
			new_entry.topic = topic
			new_entry.save()
			return redirect('learning_logs:topic', topic_id=topic_id)

	#вывести пустую или недействительную форму.
	context = {'topic': topic, 'form': form}
	return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
	"""Редактирует существующую запись."""
	entry = get_object_or_404(Entry, id=entry_id)
	topic = entry.topic
	check_topic_owner(topic.owner, request)

	if request.method !='POST':
		#Исходный запрос; форма заполняется данными текущей записи.
		form = EntryForm(instance=entry)
	else:
		#Отправка данных POST; Обработать данные.
		form = EntryForm(instance=entry, data=request.POST)
		if form.is_valid():
			form.save()
			return redirect('learning_logs:topic', topic_id=topic.id)

	context = {'entry': entry, 'topic': topic, 'form': form}
	return render(request, 'learning_logs/edit_entry.html', context)

def check_topic_owner(owner, request):
	if owner != request.user:
		raise Http404
