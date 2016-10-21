from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user
from django.http import HttpResponseRedirect, Http404
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from braces import views
from .models import Profile, Relationship
from .forms import RegisterForm, LoginForm
from .mixins import ProfileGetObjectMixin


class RegisterView(
    views.AnonymousRequiredMixin,
    views.FormValidMessageMixin,
    generic.CreateView
):
    model = Profile
    form_class = RegisterForm
    form_valid_message = "Successfully created your account"
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/register.html'

    def form_valid(self, form):
        # self.object = form.save(self.request)
        self.object = form.save(commit=False)

        # avatar = Profile(
        #     avatar=self.get_form_kwargs().get('files')['avatar'])
        # avatar.save()
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS, "Registration completed! Now log in")
        return super(RegisterView, self).form_valid(form)


class LoginProfileView(
    views.AnonymousRequiredMixin,
    generic.FormView
):
    form_class = LoginForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user and user.is_active:
            login(self.request, user)
            messages.add_message(self.request, messages.SUCCESS, "Great! Now you can use this service"
                                                                 "like a pro")
            return super(LoginProfileView, self).form_valid(form)
        else:
            return self.form_invalid(form)


class LogoutProfile(generic.View):
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, "You've logged out successfully")
        return redirect(reverse_lazy('accounts:register'))


class ProfileDetailView(
    views.LoginRequiredMixin,
    ProfileGetObjectMixin,
    generic.DetailView
):
    model = Profile
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'accounts/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        username = self.kwargs['username']
        self_user = self.request.user
        user = get_object_or_404(Profile, username=username)

        context['user'] = user
        context['self_user'] = self_user
        context['followers_count'] = user.get_followers_count()
        context['followings_count'] = user.get_followings_count()
        context['new_users'] = Profile.objects.order_by('-registration_date')[:5]

        if self_user.get_followings().filter(following__username=user.username).exists():
            is_following = True
        else:
            is_following = False

        context['is_following'] = is_following
        return context


class ProfileUpdateView(
    views.LoginRequiredMixin,
    generic.UpdateView,
):
    # model = Profile
    # form_class =
    pass


class FollowersListView(
    views.LoginRequiredMixin,
    generic.ListView
):
    model = Profile
    template_name = "accounts/followers_list.html"
    context_object_name = "followers"
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs['username']
        user_object = Profile.objects.get(username=username)
        self_user = self.request.user
        return user_object.get_followers()


class FollowingsListView(
    views.LoginRequiredMixin,
    generic.ListView
):
    model = Profile
    template_name = "accounts/followings_list.html"
    context_object_name = "followings"
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs['username']
        user_object = Profile.objects.get(username=username)
        return user_object.get_followings()


class UsersListView(
    views.LoginRequiredMixin,
    generic.ListView
):
    model = Profile
    template_name = "accounts/users_list.html"
    context_object_name = "users"
    paginate_by = 10


class FollowProfileView(
    views.LoginRequiredMixin,
    generic.View
):

    def get(self, request, *args, **kwargs):
        self_user = Profile.objects.get(username=request.user)
        try:
            follow_user = Profile.objects.get(username=kwargs['username'])
        except Profile.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Such user doesn't exist, sorry. "
                                                          "Check out users on this page")
            return redirect(reverse_lazy('accounts:users'))

        if self_user.id == follow_user.id:
            messages.add_message(request, messages.ERROR, "Follow yourself, seriously?")
            redirect(self_user.get_absolute_url())

        else:
            follow_action, created = Relationship.objects.get_or_create(follower=self_user,
                                                                        following=follow_user)

            if created:
                messages.add_message(request, messages.SUCCESS,
                                     "Yeap, now you are following {}".format(follow_user.username))

            else:
                messages.add_message(request, messages.ERROR,
                                     "You've already followed user {}".format(follow_user.username))

        return redirect(self_user.get_absolute_url())

    def post(self, request, **kwargs):
        self_user = Profile.objects.get(username=request.user)
        print(self_user)
        return redirect(self_user.get_absolute_url())


class UnfollowProfileView(
    views.LoginRequiredMixin,
    generic.View
):
    # will reverse methods in production, now this is for testing purposes
    def get(self, request, *args, **kwargs):
        self_user = Profile.objects.get(username=request.user)
        try:
            unfollow_user = Profile.objects.get(username=kwargs['username'])
        except Profile.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Such user doesn't exist, sorry. "
                                                          "Check out users on this page")
            return redirect(reverse_lazy('accounts:users'))

        if self_user.id == unfollow_user.id:
            messages.add_message(request, messages.ERROR, "Unfollow yourself, seriously?")
            redirect(self_user.get_absolute_url())
        else:
            try:
                unfollow_action = Relationship.objects.get(follower=self_user, following=unfollow_user)
            except Relationship.DoesNotExist:
                messages.add_message(request, messages.ERROR, "First you need to follow this user!")
                return redirect(unfollow_user.get_absolute_url())
            unfollow_action.delete()
            messages.add_message(request, messages.SUCCESS, "Successfully unfollowed "
                                                          "{}".format(unfollow_user))
        return redirect(self_user.get_absolute_url())

    def post(self, request, **kwargs):
        self_user = Profile.objects.get(username=request.user)
        messages.add_message(request, messages.INFO, "To unfollow user use POST request ")
        return redirect(self_user.get_absolute_url())

