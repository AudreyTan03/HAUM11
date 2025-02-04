from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from item.models import Item
from profile.forms import UserUpdateForm, ProfileUpdateForm, ColorPreferenceForm, FontPreferenceForm
from profile.models import Profile, UserVote, Location
# from .models import LoginHistory # Import your LoginHistory model


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    color_form = ColorPreferenceForm(instance=profile)
    locations = Location.objects.all()
    font_form = FontPreferenceForm(instance=request.user.profile)
    login_history = user.active_logins
    print(login_history)

    if request.method == 'POST':
        print("post method")
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES,
                                   instance=request.user.profile)
        font_form = FontPreferenceForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid() and font_form.is_valid():
            # request.user.save()
            print("valid form")
            u_form.save()
            p_form.save()
            font_form.save()
            # # profile.color = form.cleaned_data['color']
            # color_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile', request.user.username)
    else:
        user = User.objects.get(username=username)
        form = FontPreferenceForm(instance=request.user.profile)
        profile = Profile.objects.get(user=user)
        print(user.first_name)
        print(profile.first_name)
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)

    user_profile_color = profile.color
    is_own_profile = user == request.user
    print(user_profile_color)
    # Fetch items based on the condition
    if not is_own_profile:
        item = Item.objects.filter(created_by=user)
    else:
        item = None

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'bio': profile.bio,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'address': profile.address,
        'user': user,
        'profile': profile,
        'item': item,
        'is_own_profile': is_own_profile,
        'user_profile_color': user_profile_color,

        # Instantiating the font_form in the start of the function
        'form': font_form,

        'locations': locations,
        'color_form': color_form,
        'login_history': login_history

    }

    return render(request, 'profile/profile.html', context)


# GINALAW NO VOTE OWN
# Upvote view
@login_required
def upvote(request, username):
    user = request.user  # The user who is upvoting (logged-in user)
    target_user = User.objects.get(username=username)  # The user who is being upvoted
    target_profile = Profile.objects.get(user=target_user)  # The profile of the user who is being upvoted

    if user == target_user:
        messages.error(request, "You cannot vote your own profile.")
        return redirect('profile', username=username)

    try:
        user_vote = UserVote.objects.get(voter=user, profile=target_profile)  # Check if the user has voted before
        if user_vote.is_upvote:  # Check if the user has upvoted before
            # The user has upvoted, so remove the vote
            user_vote.delete()  # Delete the vote
            if target_profile.upvotes > 0:  # Ensure upvotes is not negative
                target_profile.upvotes -= 1  # Decrement the upvotes
                target_profile.save()  # Save the changes
            messages.success(request, f'You have removed your upvote for {target_user.username}!')
        else:
            # The user has downvoted, so change the vote to upvote
            user_vote.is_upvote = True  # Change the vote to upvote
            user_vote.save()
            if target_profile.downvotes > 0:  # Ensure downvotes is not negative
                target_profile.downvotes -= 1  # Decrement the downvotes
            target_profile.upvotes += 1  # Increment the upvotes
            target_profile.save()  # Save the changes
            messages.success(request, f'You have changed your vote to an upvote for {target_user.username}!')
    except UserVote.DoesNotExist:
        # The user hasn't voted before, so create a new upvote
        user_vote = UserVote(voter=user, profile=target_profile, is_upvote=True)  # Create a new upvote
        user_vote.save()  # Save the upvote
        target_profile.upvotes += 1  # Increment the upvotes
        target_profile.save()  # Save the changes
        messages.success(request, f'You have upvoted {target_user.username}!')  # Display a success message

    return redirect('profile', username=username)  # Redirect to the profile page of the user who is being upvoted


# Downvote view
@login_required
def downvote(request, username):
    user = request.user
    target_user = User.objects.get(username=username)
    target_profile = Profile.objects.get(user=target_user)

    if user == target_user:
        messages.error(request, "You cannot vote your own profile.")
        return redirect('profile', username=username)

    try:
        user_vote = UserVote.objects.get(voter=user, profile=target_profile)
        if not user_vote.is_upvote:
            # The user has downvoted, so remove the vote
            user_vote.delete()
            if target_profile.downvotes > 0:  # Ensure downvotes is not negative
                target_profile.downvotes -= 1
                target_profile.save()
            messages.success(request, f'You have removed your downvote for {target_user.username}!')
        else:
            # The user has upvoted, so change the vote to downvote
            user_vote.is_upvote = False
            user_vote.save()
            if target_profile.upvotes > 0:  # Ensure upvotes is not negative
                target_profile.upvotes -= 1
            target_profile.downvotes += 1
            target_profile.save()
            messages.success(request, f'You have changed your vote to a downvote for {target_user.username}!')
    except UserVote.DoesNotExist:
        # The user hasn't voted before, so create a new downvote
        user_vote = UserVote(voter=user, profile=target_profile, is_upvote=False)
        user_vote.save()
        target_profile.downvotes += 1
        target_profile.save()
        messages.success(request, f'You have downvoted {target_user.username}!')

    return redirect('profile', username=username)


 # Import your LoginHistory model


# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from .models import LoginHistory  # Import your LoginHistory model
#
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# from .models import LoginHistory  # Import your LoginHistory model

# def user_profile(request):
#     login_history = LoginHistory.objects.filter(user=request.user).order_by('-date_time')
#
#     # Number of items to display per page
#     items_per_page = 5
#
#     # Create a Paginator object
#     paginator = Paginator(login_history, items_per_page)
#
#     # Get the page number from the request's GET parameters
#     page = request.GET.get('page')
#
#     try:
#         # Attempt to convert the page parameter to an integer
#         page = int(page)
#     except (ValueError, TypeError):
#         # Handle non-integer or missing page parameter by showing the first page
#         page = 1
#
#     try:
#         # Get the Page object for the requested page
#         login_history = paginator.page(page)
#     except PageNotAnInteger:
#         # If the page is not an integer, show the first page
#         login_history = paginator.page(1)
#     except EmptyPage:
#         # If the page is out of range, for example, 1000, redirect to the last page
#         login_history = paginator.page(paginator.num_pages)
#
#     return render(request, 'profile.html', {'login_history': login_history})
#
#
#
#

