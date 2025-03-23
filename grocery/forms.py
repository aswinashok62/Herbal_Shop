from django import forms
from .models import ProductRequest

class ProductRequestForm(forms.ModelForm):
    class Meta:
        model = ProductRequest
        fields = ['product_name', 'category', 'quantity', 'supplier']

from django import forms
from .models import RefundRequest

class RefundForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['account_name', 'account_number', 'bank_name', 'ifsc_code']


from django import forms
from .models import Chat

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ["message", "file"]
