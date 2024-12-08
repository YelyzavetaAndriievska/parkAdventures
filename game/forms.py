from django import forms
from django.contrib.auth.models import User
import random
import string

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.set_password(password)
        if commit:
            user.save()
        return user, password
class ResourceInputForm(forms.Form):
    input_text = forms.CharField(max_length=100, required=True)