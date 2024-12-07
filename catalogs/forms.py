from django import forms
from catalogs.models import AttendanceTask, Catalog

class ActiveCatalogForm(forms.ModelForm):
    class Meta:
        model = AttendanceTask
        fields = ['task', 'note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task'].queryset = Catalog.objects.filter(is_active=True)
