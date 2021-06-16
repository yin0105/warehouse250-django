from django import forms

from .models import District, Sector, Cell, Village, DeliveryCost

class CheckoutForm(forms.Form):

    district = forms.ChoiceField(choices=[(-1, '')] + [(entry.id, entry.district) for entry in District.objects.all()])

    sector = forms.ChoiceField(choices=[(-1, '')] + [(entry.id, entry.sector) for entry in Sector.objects.all()])

    cell = forms.ChoiceField(choices=[(-1, '')] + [(entry.id, entry.cell) for entry in Cell.objects.all()])

    village = forms.ChoiceField(choices=[(-1, '')] + [(entry.id, entry.village) for entry in Village.objects.all()])

    delivery_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 85}), max_length=170)

    # delivery_cost = forms.ChoiceField(choices=[(entry.id, entry.cost) for entry in DeliveryCost.objects.all()])
    
    delivery_option = forms.ChoiceField(widget=forms.RadioSelect, choices=[('Store', 'Pick up from Store'), ('Basic_Delivery', 'Basic delivery'), ('Express_Delivery', 'Express delivery')])

class PaymentForm(forms.Form):
    stripe_token = forms.CharField(max_length=255)
