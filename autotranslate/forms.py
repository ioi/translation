from django import forms
from autotranslate import get_supported_languages

class TranslateRequestForm(forms.Form):
    input_lang = forms.ChoiceField(choices=get_supported_languages())
    output_lang = forms.ChoiceField(choices=get_supported_languages())
    content = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        input_lang = cleaned_data.get("input_lang")
        output_lang = cleaned_data.get("output_lang")
        if input_lang == output_lang:
            raise forms.ValidationError("Target language must be different from source langauge.")
        
        return cleaned_data