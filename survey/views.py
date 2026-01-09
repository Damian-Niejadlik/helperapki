from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SurveyForm
from .services import save_entry

def index(request):
    # Default mode is empty until selected, or you can default to 'normal'
    selected_mode = request.GET.get('mode')
    
    valid_modes = ['normal', 'funny', 'strange']
    if selected_mode and selected_mode not in valid_modes:
        selected_mode = None

    if request.method == 'POST':
        form = SurveyForm(request.POST)
        current_mode = request.POST.get('active_mode') # Pass mode via hidden input or action
        
        if form.is_valid() and current_mode in valid_modes:
            try:
                questions_list = form.get_questions_list()
                location = form.cleaned_data['location']
                
                # Save to cloud
                save_entry(current_mode, location, questions_list)
                
                messages.success(request, 'Form submitted successfully!')
                return redirect(f'/?mode={current_mode}')
            except Exception as e:
                messages.error(request, f'Error saving data: {str(e)}')
        else:
             messages.error(request, 'Please fill all fields.')
    else:
        form = SurveyForm()
        current_mode = selected_mode

    return render(request, 'survey/index.html', {
        'form': form,
        'mode': current_mode,
        'modes': valid_modes
    })
