from django import forms


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField()

class AddToCartInListForm(forms.Form):
    slug = forms.CharField(max_length=50)
