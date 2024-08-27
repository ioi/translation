from django import forms
from autotranslate import get_supported_languages

class TranslateRequestForm(forms.Form):
    input_lang = forms.ChoiceField(choices=get_supported_languages())
    output_lang = forms.ChoiceField(choices=get_supported_languages())
    content = forms.CharField()
