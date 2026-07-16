
from django import forms
from .models import Payment, Expenditure


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'category', 'amount', 'payment_date', 'method', 'proof_image', 'month', 'year', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ExpenditureForm(forms.ModelForm):
    class Meta:
        model = Expenditure
        fields = ['title', 'amount', 'date', 'description', 'receipt']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }