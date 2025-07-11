# tasks > forms.py
from django import forms
from tasks.models import Task, TaskDetail
from django.contrib.auth import get_user_model

User = get_user_model()
# forms.ModelForm vs forms.Form (manually construct/save the model instance in view, including M2M relationships)

"""
# also worked
class TaskForm(forms.Form):
    title = forms.CharField(max_length=250, label="Task Title")
    description = forms.CharField(widget=forms.Textarea, label='Task Description')        
    due_date = forms.DateField(widget=forms.SelectDateWidget, label="Due Date")
    assigned_to = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=[], label='Assigned To')
    def __init__(self, *args, **kwargs):
        # changed
        employees = kwargs.pop("employees", None)  # pop to not send it to super
        super().__init__(*args, **kwargs)  # here unpacks with * and **
        # print(self.fields)
        if employees is not None:
            #self.fields['assigned_to'].queryset = employees  # shows empty in form page
            self.fields['assigned_to'].choices = [(emp.id, emp.username) for emp in employees]
        else:
            active_users = User.objects.filter(is_active=True)    
            self.fields['assigned_to'].choices = [(emp.id, emp.username) for emp in active_users]
"""

class TaskForm(forms.Form):
    title = forms.CharField(
        max_length=250,
        label="Task Title",
        widget=forms.TextInput(attrs={
            'class': 'block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring focus:ring-indigo-200 focus:border-indigo-300 mb-1'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring focus:ring-indigo-200 focus:border-indigo-300 mb-4',
            'rows': 4,
        }),
        label='Task Description'
    )      
    due_date = forms.DateField(widget=forms.SelectDateWidget, label="Due Date")
    assigned_to = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=[], label='Assigned To')

    def __init__(self, *args, **kwargs):
        # print(args, kwargs)
        employees = kwargs.pop("employees", [])
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].choices = [(emp.id, emp.username) for emp in employees]  # list comprehension
            

# Mixing to apply style to form field,
class StyledFormMixin:
    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)  # MRO: Method Resolution Order, here, calls init of forms.ModelForm
        self.apply_styled_widgets()

    default_classes = "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-cyan-500 mb-1"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    #'class': self.default_classes,
                    'class': 'block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring focus:ring-indigo-200 focus:border-indigo-300 mb-1',
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': self.default_classes, 
                    'placeholder':  f"Enter {field.label.lower()}",
                    'rows': 3
                })
            elif isinstance(field.widget, forms.SelectDateWidget):
                # print("Inside Date")
                field.widget.attrs.update({
                    "class": "border-2 border-gray-300 p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500"
                })
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                # print("Inside checkbox")
                field.widget.attrs.update({
                    'class': "space-y-2"
                })
            else:
                # print("Inside else")
                field.widget.attrs.update({
                    'class': self.default_classes
                })


import datetime

class TaskModelForm(StyledFormMixin, forms.ModelForm): # mixin at first
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'assigned_to', 'project']
        # exclude = ["is_completed", "created_at", "updated_at"]
        widgets = {
            'due_date': forms.SelectDateWidget(years=range(datetime.date.today().year, datetime.date.today().year + 30)),
            'assigned_to': forms.CheckboxSelectMultiple
        }


class TaskDetailModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = TaskDetail
        fields = ['priority', 'notes', 'asset']