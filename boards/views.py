from django.shortcuts import render,HttpResponse,get_object_or_404,redirect
from .models import Board,User,Topic,Post
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import NewTopicForm, NewBoard,PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import View, UpdateView,ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
# Create your views here.
def home(request):
    boards = Board.objects.all()
    return render(request,'home.html',{'boards':boards})

class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'
def board_topics(request,pk):
    board = get_object_or_404(Board, pk=pk)
    queryset = board.topics.order_by('-last_update').annotate(replies=Count('posts') - 1)
    page = request.GET.get('page', 1)

    paginator = Paginator(queryset, 20)

    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        topics = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        topics = paginator.page(paginator.num_pages)

    return render(request, 'topics.html', {'board': board, 'topics': topics})

def addboard(request):
    if request.method == 'POST':
        form = NewBoard(request.POST)
        if form.is_valid():
            board =form.save()
            board.save()
            return redirect('home')
    else:
        form = NewBoard()
    return render(request,'addboard.html',{'form':form})

@login_required
def new_topic(request,pk):
    board = get_object_or_404(Board,pk = pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.starter = request.user
            topic.board = board
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)  # TODO: redirect to the created topic page
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})

@login_required
def topic_posts(request,pk,topic_pk):
    topic = get_object_or_404(Topic,board__pk = pk,pk = topic_pk)
    topic.views = topic.views+1
    topic.save()
    return render(request,'topic_posts.html',{'topic':topic})

@login_required
def reply_topic(request,pk,topic_pk):
    topic = get_object_or_404(Topic, board__pk = pk,pk = topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit = False)
        post.update_by = self.request.user
        post.update_at = timezone.now()
        form.save()
        return redirect('topic_posts', pk = post.topic.board.pk, topic_pk = post.topic.pk)
