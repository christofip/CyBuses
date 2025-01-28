from django import forms
from .models import Stop, Route

class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = ['code', 'description', 'description_el', 'description_en', 'location']

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = [
            'route_id', 'line_name', 'route_name', 'direction', 'length',
            'first_stop', 'last_stop', 'stops_list', 'geometry', 'color',
            'weekday_start', 'weekday_end',
            'saturday_start', 'saturday_end',
            'holiday_start', 'holiday_end'
        ] 