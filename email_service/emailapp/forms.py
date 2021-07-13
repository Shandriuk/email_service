
# sendemail/forms.py
from django import forms
from .models import Receiver

"""class EmailForm1(forms.ModelForm):

    class Meta:
        model = Receiver
        fields = "__all__"
        widgets = {"email": forms.EmailField(),
            "name": forms.EmailField(),
            "surname": forms.EmailField(),
            "bday": forms.EmailField()
        }
        """
class EmailForm(forms.Form):
        email= forms.EmailField()
        name= forms.CharField()
        surname= forms.CharField()
        bday= forms.DateField(widget=forms.SelectDateWidget())
