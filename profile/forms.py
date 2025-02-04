from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username']

# form eto para ma change update yung user profile mo
#GINALAW
class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = Profile
        fields = ['bio', 'address', 'location', 'image', 'color', 'font_preference']

    def save(self, commit=True):
        profile = super(ProfileUpdateForm, self).save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            profile.save()

        return profile


#Color Preference Form can be deleted since the color field is already in the ProfileUpdateForm
class ColorPreferenceForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['color']


class FontPreferenceForm(forms.ModelForm):
    FONT_CHOICES = (
        ('Young Serif', 'Young Serif'),
        ('Roboto Slab', 'Roboto Slab'),
        ('Noto Sans JP', 'Noto Sans JP'),
        ('Yuji Hentaigana Akari', 'Yuji Hentaigana Akari'),
    )
    # Replaced the font field with choices added new font option

    # Add the font field with choices
    font_preference = forms.ChoiceField(
        choices=FONT_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Profile
        fields = ['font_preference']
