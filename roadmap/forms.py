from django import forms
from .models import StudentProfile


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["current_skills", "education", "interests", "target_job"]
        widgets = {
            "current_skills": forms.TextInput(
                attrs={"placeholder": "e.g. Python, SQL", "class": "input"}
            ),
            "education": forms.TextInput(
                attrs={"placeholder": "e.g. B.Tech Computer Science", "class": "input"}
            ),
            "interests": forms.TextInput(
                attrs={"placeholder": "e.g. Data, Automation, AI", "class": "input"}
            ),
            "target_job": forms.TextInput(
                attrs={"placeholder": "e.g. Data Analyst", "class": "input"}
            ),
        }
