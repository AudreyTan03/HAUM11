from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from item.models import Item
from profile.forms import UserUpdateForm, ProfileUpdateForm, ColorPreferenceForm, FontPreferenceForm
from profile.models import Profile, UserVote, Location


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    color_form = ColorPreferenceForm(instance=profile)
    locations = Location.objects.all()
    font_form = FontPreferenceForm(instance=request.user.profile)

    if request.method == 'POST':
        print("post method")
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES,
                                   instance=request.user.profile)
        # print(request.POST)
        # color_form = ColorPreferenceForm(request.POST, instance=profile)
        # Removed the color form. Not needed since it is being called from the p_form
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
        print(user)
        print(profile)
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
        'firstname': profile.firstname,
        'lastname': profile.lastname,
        'address': profile.address,
        'user': user,
        'profile': profile,
        'item': item,
        'is_own_profile': is_own_profile,
        'user_profile_color': user_profile_color,

        # Instantiating the font_form in the start of the function
        'form': font_form,

        'locations': locations,
        'color_form': color_form

    }

    return render(request, 'profile/profile.html', context)

# Upvote view
@login_required
def upvote(request, username):
    user = request.user
    target_user = User.objects.get(username=username)
    target_profile = Profile.objects.get(user=target_user)

    try:
        user_vote = UserVote.objects.get(voter=user, profile=target_profile)
        if user_vote.is_upvote:
            # The user has upvoted, so remove the vote
            user_vote.delete()
            if target_profile.upvotes > 0:  # Ensure upvotes is not negative
                target_profile.upvotes -= 1
                target_profile.save()
            messages.success(request, f'You have removed your upvote for {target_user.username}!')
        else:
            # The user has downvoted, so change the vote to upvote
            user_vote.is_upvote = True
            user_vote.save()
            if target_profile.downvotes > 0:  # Ensure downvotes is not negative
                target_profile.downvotes -= 1
            target_profile.upvotes += 1
            target_profile.save()
            messages.success(request, f'You have changed your vote to an upvote for {target_user.username}!')
    except UserVote.DoesNotExist:
        # The user hasn't voted before, so create a new upvote
        user_vote = UserVote(voter=user, profile=target_profile, is_upvote=True)
        user_vote.save()
        target_profile.upvotes += 1
        target_profile.save()
        messages.success(request, f'You have upvoted {target_user.username}!')

    return redirect('profile', username=username)

# Downvote view
@login_required
def downvote(request, username):
    user = request.user
    target_user = User.objects.get(username=username)
    target_profile = Profile.objects.get(user=target_user)

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
