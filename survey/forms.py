from django import forms

class SurveyForm(forms.Form):
    location = forms.CharField(
        label="Location",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded mb-4', 'placeholder': 'Enter your location...'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add 49 question fields
        for i in range(1, 50):
            field_name = f'question_{i}'
            self.fields[field_name] = forms.CharField(
                label=f'Question {i}',
                required=True,
                widget=forms.TextInput(attrs={
                    'class': 'w-full p-2 border rounded',
                    'placeholder': f'Answer for question {i}...'
                })
            )

    def get_questions_list(self):
        """Helper to return list of answers in order 1-49"""
        return [self.cleaned_data[f'question_{i}'] for i in range(1, 50)]
