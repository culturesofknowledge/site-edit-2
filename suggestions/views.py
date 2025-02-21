import time
from functools import reduce
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Q
from django.contrib import messages

from .models import CofkSuggestions
from .forms import SuggestionForm, SuggestionFilterForm

template_list = "suggestion_list.html" # Home page listing all suggestions for user
template_form = "suggestion_form.html" # Page for making a suggestion
template_view = "suggestion_view.html" # Page to display a single record
message_noupdate = "Form was not updated. Please try again."

# For query ordering, look at :
# https://docs.djangoproject.com/en/dev/ref/models/querysets/#order-by


# Common function to save the suggestion and fill in the context
def save_fill_context(request, context, edit=False):
    suggestion = context['sug_inst']
    if not edit:
        suggestion.suggestion_author = request.user
        context['message'] = "Thank you for your suggestion!"
        if context.get('record_id', None):
            suggestion.suggestion_new = False
        else:
            suggestion.suggestion_new = True
    else:
        context['message'] = f"Thank you for your update to suggestion {suggestion.suggestion_id}"
        # suggestion.suggestion_author = context['author']
        # suggestion.suggestion_updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
    # content_type = ContentType.objects.get_for_model(CofkSuggestions)
    suggestion.suggestion_suggestion = request.POST.get('suggestion_text')
    suggestion.save() # Save the suggestion to the database

    return context

def save_with_related_info(suggestion_id, related_id):
    sug = CofkSuggestions.objects.get(pk=suggestion_id)
    sug.suggestion_related_record_int = related_id
    sug.suggestion_status = "Resolved"
    sug.save()
    return

# Suggest a person
def suggestion_person(request):
    sug = CofkSuggestions()
    sug.suggestion_type = "Person"
    initial_suggestion_txt = sug.new_suggestion_text()
    context = { 'form': SuggestionForm() }
    context['sug_inst'] = sug
    context['form'].fields['suggestion_text'].initial = initial_suggestion_txt
    # The form for submitting
    if request.method == 'GET':
        return render(request, template_form, context)
    # Save submitted person form
    elif request.method == 'POST':
        if request.POST.get('suggestion_text') != initial_suggestion_txt:
            # There was something changed in the form
            context = save_fill_context(request, context)
            messages.success(request, context['message'])
            return redirect("suggestions:suggestion_all")
        else:
            # The form was not changed. Go back to the form.
            messages.warning(request, message_noupdate)
            return render(request, template_form, context)
    else:
        return HttpResponse(f"Error: Invalid request method: {request.method}")


# Suggest a place
def suggestion_location(request):
    sug = CofkSuggestions()
    sug.suggestion_type = "Location"
    initial_suggestion_txt = sug.new_suggestion_text()
    context = { 'form': SuggestionForm() }
    context['sug_inst'] = sug
    context['form'].fields['suggestion_text'].initial = initial_suggestion_txt
    if request.method == 'GET':
        return render(request, template_form, context)
    elif request.method == 'POST':
        if request.POST.get('suggestion_text') != initial_suggestion_txt:
            context = save_fill_context(request, context)
            messages.success(request, context['message'])
            return redirect("suggestions:suggestion_all")
        else:
            messages.warning(request, message_noupdate)
            return render(request, template_form, context)
    else:
        return HttpResponse(f"Error: Invalid request method: {request.method}")


# Suggest a publication
def suggestion_publication(request):
    sug = CofkSuggestions()
    sug.suggestion_type = "Publication"
    initial_suggestion_txt = sug.new_suggestion_text()
    context = { 'form': SuggestionForm() }
    context['sug_inst'] = sug
    context['form'].fields['suggestion_text'].initial = initial_suggestion_txt
    if request.method == 'GET':
        return render(request, template_form, context)
    elif request.method == 'POST':
        if request.POST.get('suggestion_text') != initial_suggestion_txt:
            context = save_fill_context(request, context)
            messages.warning(request, context['message'])
            return redirect("suggestions:suggestion_all")
        else:
            messages.success(request, message_noupdate)
            return render(request, template_form, context)
    else:
        return HttpResponse(f"Error: Invalid request method: {request.method}")


# Suggest an institution
def suggestion_institution(request):
    sug = CofkSuggestions()
    sug.suggestion_type = "Institution"
    initial_suggestion_txt = sug.new_suggestion_text()
    context = { 'form': SuggestionForm() }
    context['sug_inst'] = sug
    context['form'].fields['suggestion_text'].initial = initial_suggestion_txt
    if request.method == 'GET':
        return render(request, template_form, context)
    elif request.method == 'POST':
        if request.POST.get('suggestion_text') != initial_suggestion_txt:
            context = save_fill_context(request, context)
            messages.success(request, context['message'])
            return redirect("suggestions:suggestion_all")
        else:
            messages.warning(request, message_noupdate)
            return render(request, template_form, context)
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
    messages.success(request, f"Suggestion {suggestion_id} was successfully deleted.")
    return redirect("suggestions:suggestion_all")


def suggestion_edit(request, suggestion_id):
    # Edit the suggestion with the given unique ID
    sug = CofkSuggestions.objects.get(pk=suggestion_id)
    context = { 'form': SuggestionForm() }
    initial_suggestion_txt = sug.suggestion_suggestion
    context['sug_inst'] = sug
    context['form'].fields['suggestion_text'].initial = initial_suggestion_txt
    if request.method == 'GET':
        return render(request, template_form, context)
    elif request.method == 'POST':
        if request.POST.get('suggestion_text') != initial_suggestion_txt:
            context = save_fill_context(request, context, edit=True)
            messages.success(request, context['message'])
            return redirect("suggestions:suggestion_all")
        else:
            messages.warning(request, f"The suggestion was not updated. No change in form.")
            return render(request, template_form, context)
    else:
        return HttpResponse(f"Error: Invalid request method: {request.method}")


def suggestion_show(request, suggestion_id):
    # Show the suggestion with the given unique ID
    if request.method != 'GET': # Should be called only on a GET
        return HttpResponse(f"Error: Invalid request method: {request.method}")
    context = { 'form': SuggestionForm() }
    record = CofkSuggestions.objects.get(pk=suggestion_id)
    context['record'] = record
    return render(request, template_view, context)


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
    query_null = Q()
    # Special query - Limit data to only the current user
    query_s = Q(suggestion_author=request.user.username)
    query_r = query_null # Type of record
    query_t = query_null # New or existing record

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
    context = {'form' : f_form}
    context['query_results'] = CofkSuggestions.objects.filter(combined_q).order_by('-suggestion_id')
    return render(request, template_list, context)
