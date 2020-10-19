from django import forms
class test(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    text = forms.CharField(widget = forms.Textarea)
class search_form(forms.Form):
    keyword = forms.CharField(label="")
class ss(forms.Form):
    sh = forms.CharField()
