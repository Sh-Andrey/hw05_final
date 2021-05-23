from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post

User = get_user_model()


def paginator_pages(request, post_list):
    """Вспомогательная функция постраничного вывода."""
    paginator = Paginator(
        post_list,
        settings.NUMBER_OF_RECORDS_ON_THE_PAGINATOR_PAGE
    )
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page


def index(request):
    post_list = Post.objects.all()
    page = paginator_pages(request, post_list)
    return render(
        request,
        'posts/index.html',
        {
            'page': page
        }
    )


def posts_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page = paginator_pages(request, posts)
    return render(
        request,
        'posts/group.html',
        {
            'group': group,
            'page': page,
        }
    )


@login_required()
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(
        request,
        'posts/new_post.html',
        {
            'form': form,
            'edit': False,
        }
    )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    page = paginator_pages(request, posts)
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=user,
                                          user=request.user).exists()
    else:
        following = None
    return render(
        request,
        'posts/profile.html',
        {
            'page': page,
            'author': user,
            'following': following,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request,
        'posts/post.html',
        {
            'post': post,
            'author': post.author,
            'form': form,
            'comments': comments,
        }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=post.author, post_id=post_id)
    return render(
        request,
        'posts/new_post.html',
        {
            'form': form,
            'post': post,
            'edit': True,
        }
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username=post.author, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page = paginator_pages(request, posts)
    return render(
        request,
        'posts/follow.html',
        {
            'page': page
        }
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    follow.delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {
            'path': request.path
        }, status=404
    )


def server_error(request):
    return render(
        request,
        'misc/500.html',
        status=500
    )
