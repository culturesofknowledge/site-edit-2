import time
from functools import reduce
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Q

from .models import CofkSuggestions
from .forms import SuggestionForm, SuggestionFilterForm
from . import texts

template_base = "suggestion_listAll.html" # Home page listing all suggestions for user
template_full = "suggestion_full.html" # Page for making a suggestion
template_unique = "suggestion_unique.html" # Page to display a single record
message_noupdate = "Form was not updated. Please try again."

# For query ordering, look at :
# https://docs.djangoproject.com/en/dev/ref/models/querysets/#order-by

# Common function to save the suggestion and fill in the context
def save_fill_context(request, context, edit=False):
    cus = CofkSuggestions()
    content_type = ContentType.objects.get_for_model(CofkSuggestions)
    cus.suggestion_suggestion = request.POST.get('suggestion_text')
    cus.suggestion_type = context['type']
    cus.suggestion_author = request.user
    if 'suggestion_new' in context.keys(): # This is an edit in spite of the name
        cus.suggestion_id = context['suggestion_id']
        cus.suggestion_new = context['suggestion_new']
        cus.suggestion_author = context['author']
        cus.suggestion_updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        cus.suggestion_created_at = context['date_creation']
        cus.suggestion_status = "Updated"
    cus.save() # Save the suggestion to the database
    time.sleep(2) # Sleep to allow the database to update

    context['message'] = "Thank you for your suggestion!"
    context['query_results'] = CofkSuggestions.objects.all().filter(suggestion_author=request.user).order_by('suggestion_id')
    return context

# Suggest a person
def suggestion_person(request):
    context = { 'form': SuggestionForm() }
    context['type'] = "Person"
    context['form'].fields['suggestion_text'].initial = texts.person_txt
    if request.method == 'GET': # The form for submitting
        return render(request, template_full, context)
    elif request.method == 'POST': # Back to the base form after submitting
        if request.POST.get('suggestion_text') != texts.person_txt:
            # There was something changed in the form
            context = save_fill_context(request, context)
            context['form'] = SuggestionFilterForm()
            return render(request, template_base, context)
        else:
            # The form was not changed. Go back to the form.
            context['message'] = message_noupdate
            return render(request, template_full, context)
    else:
        return HttpResponse(f"Error: Invalid request method: {request.method}")

# Suggest a place
def suggestion_location(request):
    context = { 'form': SuggestionForm() }
    context['type'] = "Location"
    context['form'].fields['suggestion_text'].initial = texts.location_txt
    if request.method == 'GET':
        return render(request, template_full, context)
    elif request.method == 'POST':
        if request.POST.get('suggestion_text') != texts.location_txt:
            context = save_fill_context(request, context)
            context['form'] = SuggestionFilterForm()
            return render(request, template_base, context)
        else:
            context['message'] = message_noupdate
            return render(request, template_full, context)
    else:
        return HttpResponse(f"Error: Invalid request method: {request.method}")

# Suggest a publication
def suggestion_publication(request):
    context = { 'form': SuggestionForm() }
    context['type'] = "Publication"
    context['form'].fields['suggestion_text'].initial = texts.publication_txt
    if request.method == 'GET':
        return render(request, template_full, context)
    elif request.method == 'POST':
        if request.POST.get('suggestion_text') != texts.publication_txt:
            context = save_fill_context(request, context)
            context['form'] = SuggestionFilterForm()
            return render(request, template_base, context)
        else:
            context['message'] = message_noupdate
            return render(request, template_full, context)
    else:
        return HttpResponse(f"Error: Invalid request method: {request.method}")

# Suggest an institution
def suggestion_institution(request):
    context = { 'form': SuggestionForm() }
    context['type'] = "Institution"
    context['form'].fields['suggestion_text'].initial = texts.institution_txt
    if request.method == 'GET':
        return render(request, template_full, context)
    elif request.method == 'POST':
        if request.POST.get('suggestion_text') != texts.institution_txt:
            context = save_fill_context(request, context)
            context['form'] = SuggestionFilterForm()
            return render(request, template_base, context)
        else:
            context['message'] = message_noupdate
            return render(request, template_full, context)
    else:
        return HttpResponse(f"Error: Invalid request method: {request.method}")

def suggestion_delete(request, suggestion_id):
    # Delete just the suggestion with the given unique ID
    if request.method != 'POST': # Should be called only on a POST
        return HttpResponse(f"Error: Invalid request method: {request.method}")
    context = { 'form': SuggestionForm() }
    context['type'] = "Delete"
    context['prefill'] = ""
    context['query_results'] = CofkSuggestions.objects.all().filter(suggestion_author=request.user)
    CofkSuggestions.objects.all().filter(suggestion_id=suggestion_id).delete()
    time.sleep(2) # Sleep for 2 seconds to allow the database to update
    context['message'] = f"Suggestion {suggestion_id} was successfully deleted."
    context['form'] = SuggestionFilterForm()
    return render(request, template_base, context)

def suggestion_edit(request, suggestion_id):
    # Edit the suggestion with the given unique ID
    context = { 'form': SuggestionForm() }
    # record should be a list of just one record
    record = CofkSuggestions.objects.all().filter(suggestion_id=suggestion_id)
    context['type'] = record[0].suggestion_type
    initial_save = record[0].suggestion_suggestion
    context['form'].fields['suggestion_text'].initial = initial_save
    context['suggestion_id'] = suggestion_id
    context['author'] = record[0].suggestion_author
    context['date_creation'] = record[0].suggestion_created_at
    if request.method == 'GET':
        return render(request, template_full, context)
    elif request.method == 'POST':
        if request.POST.get('suggestion_text') != initial_save:
            context['suggestion_new'] = False
            context = save_fill_context(request, context)
            context['form'] = SuggestionFilterForm()
            return render(request, template_base, context)
        else:
            context['message'] = "Suggestion was not updated. Please try again."
            return render(request, template_full, context)
    else:
        return HttpResponse(f"Error: Invalid request method: {request.method}")

def suggestion_show(request, suggestion_id):
    # Show the suggestion with the given unique ID
    if request.method != 'GET': # Should be called only on a GET
        return HttpResponse(f"Error: Invalid request method: {request.method}")
    context = { 'form': SuggestionForm() }
    record = CofkSuggestions.objects.all().filter(suggestion_id=suggestion_id)
    context['record'] = record[0]
    return render(request, template_unique, context)

def suggestion_all(request):
    # Show all the suggestions matching the requested filters
    if request.method != 'GET': # Should be called only on a GET
        return HttpResponse(f"Error: Invalid request method: {request.method}")
    f_form = SuggestionFilterForm(data=request.GET)
    # Filtering the URL
    types = ["Person", "Institution", "Location", "Publication"]
    nr_type = True # New Record
    er_type = True # Existing record

    # First set up the full query
    # Special query - Limit data to only the current user
    query_null = Q()
    query_s = Q(suggestion_author=request.user.username)
    query_r = query_null
    query_t = query_null

    # Remove the unwanted fields
    for field in f_form:
        if field.value():
            if field.name.title() in types:
                query_t = query_t | Q(suggestion_type=field.name.title())
            elif field.name == "showNew":
                query_r = query_r | Q(suggestion_new=True)
            elif field.name == "showExisting":
                query_r = query_r | ~Q(suggestion_new=True)
            else:
                print(f"Unknown search type : {field.name}")

    combined_q = query_s
    if query_r != query_null:
        combined_q = combined_q & query_r
    if query_t != query_null:
        combined_q = combined_q & query_t
    # Now we have the filtering query, actually use it
    context = { 'form': f_form }
    context['query_results'] = CofkSuggestions.objects.filter(combined_q)
    return render(request, template_base, context)
