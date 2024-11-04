from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from monitoring_app.models import *

class stage_form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["description"].required = False

    class Meta():
        model = Stage
        fields = ('description',)
        widgets = {
              "text": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5 form-control"}, config_name="special"
              )
          }
        

class update_stage_form(forms.ModelForm):
    number      = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Stage number'}))
    title       = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Stage Title'}))
    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.fields["description"].required = False

    class Meta():
        model = Stage
        fields = ('number','title','description')
        widgets = {
              "text": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5 form-control"}, config_name="special"
              )
          }