from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ProfilePictureModel, Ingredients, ReceptModel


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=20,
        label='Křestní jméno',
        widget=forms.TextInput(attrs={'placeholder': 'Křestní jméno'})
    )
    last_name = forms.CharField(
    max_length=25,
    label='Příjmení',
    widget=forms.TextInput(attrs={'placeholder': 'Příjmení'})
    )
    username = forms.CharField(
        max_length=20,
        min_length=3,
        label='Přihlašovací jméno',
        widget=forms.TextInput(attrs={'placeholder': 'Přihlašovací jméno'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'placeholder': 'E-mail'})
    )
    password1 = forms.CharField(
        min_length=8,
        label='Heslo',
        widget=forms.PasswordInput(attrs={'placeholder': 'Heslo'})
    )
    password2 = forms.CharField(
        min_length=8,
        label='Heslo znovu',
        widget=forms.PasswordInput(attrs={'placeholder': 'Heslo znovu'})
    )
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Přihlašovací jméno',
        widget=forms.TextInput(attrs={'placeholder': 'Přihlašovací jméno'})
    )
    password = forms.CharField(
        label='Heslo',
        widget=forms.PasswordInput(attrs={'placeholder': 'Heslo'})
    )

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = ProfilePictureModel
        fields = ['image']
        labels = {
            'image': 'Změnit profilový obrázek'
        }



# recepty
class ReceptForm(forms.ModelForm):
    class Meta:
        model = ReceptModel
        fields = ['title', 'description', 'ingredients', 'image', 'user_id']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Název receptu'}),
            'description': forms.Textarea(attrs={'placeholder': 'Postup přípravy'}),
            'ingredients': forms.Textarea(attrs={'placeholder': 'Ingredience'})
        }
        labels = {
            'image': 'Vyber fotku:'
        }


class IngredientsForm(forms.Form):
    ingredients_selection = forms.ModelMultipleChoiceField(
        queryset=Ingredients.objects.none(),  # Dočasně prázdné
        widget=forms.CheckboxSelectMultiple,
        label='Vyberte ingredience'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # získej uživatele z argumentů
        super().__init__(*args, **kwargs)
        self.fields['ingredients_selection'].queryset = Ingredients.objects.filter(user_id=user.id).order_by('name')