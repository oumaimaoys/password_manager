from .models import User, Account, Platform
from django import forms
from django.forms import ModelForm

# model Forms

class UserForm(ModelForm):
    class Meta:
        model = User
        fields= ["first_name", "last_name"]
        widgets = {'user_name': forms.HiddenInput(), 'password':forms.HiddenInput()}


class AccountForm(ModelForm):
    platforms = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=Platform.objects.all())
    class Meta:
        model = Account
        fields = ["user","platforms"]
        exclude = ["status"]
        widgets = {'platform' : forms.HiddenInput()}