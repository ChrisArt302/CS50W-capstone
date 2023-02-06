from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.urls import reverse
from .models import User, Events
from django import forms
from django.forms import ModelForm
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
import smtplib
from datetime import date, datetime, timedelta, time
#import datetime
import pytz
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import json
# Initialize environment variables
import environ
env = environ.Env()
environ.Env.read_env()

class EventForm(ModelForm):
    class Meta:
        model = Events
        fields = ['title', 'description','host', 'attendees', 'date', 'start', 'end', 'category', 'number_attending', 'location', 'image']
        labels = {
            }
    
    # widget for durationfield django?
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'host': forms.TextInput(attrs={'class': 'form-control', 'type':'hidden'}),
            'attendees': forms.TextInput(attrs={'class': 'form-control', 'type':'hidden'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type':'date', 'placeholder':'date.today()'}),
            'start': forms.TimeInput(attrs={'class': 'form-control', 'type':'time'}),
            'end': forms.TimeInput(attrs={'class': 'form-control', 'type':'time'}),
            'timestamp':forms.DateTimeInput(attrs={'class': 'form-control', 'type':'hidden'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'number_attending': forms.NumberInput(attrs={'class': 'form-control', 'type':'hidden', 'value':'1'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'type':'text','id':'autocomplete'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'type':'file'}),
            }
    # function used for validation
    def clean(self):
        # data is fetched with super function
        super(EventForm, self).clean()

        # extract select fields from data
        title = self.cleaned_data.get('title')
        description = self.cleaned_data.get('description')
        date = self.cleaned_data.get('date')
        start = self.cleaned_data.get('start')
        end = self.cleaned_data.get('end')
        print('start', start, 'end', end)
        
        try:
            result = datetime.combine(date.today(), start) 
            #+ \ 
            # timedelta(hours=1)
            print("Result", result)

            only_t = result.time()
            print("Answer1:", only_t)
            
            endtime = datetime.combine(date.today(), end)
            difference = endtime - result
            example = difference.total_seconds()
            minutes = divmod(example, 60)[0]
            print("Minutes", minutes)
            if minutes < 60.0:
                self._errors['end'] = self.error_class([
                "Minimum one hour per event"])
                print("Minimum one h")
        except:
            pass

        # conditions 
        if len(title) < 4:
            self._errors['title'] = self.error_class([
                'Minimum 4 characters required for Title'])
            print('Error with title found')
        if len(description) < 4:
            self._errors['description'] = self.error_class([
                'Minimum 4 characters required for Description'])
            print('Error with desc. found')
        
        date_obj = datetime.now(pytz.timezone('US/Pacific'))
        today = date_obj.date()
        print(today, date )
        future = today + timedelta(days=1)

        if date >= future:
            print('solution') 
        if date <= today:
            self._errors['date'] = self.error_class([
                'Please enter a future date'])
            print('Error with date found')
        
        # checks for future time
        if start >= end:
            self._errors['end'] = self.error_class([
                'Please enter a future time'])
            print("Error with end time")

        # Model
        mymodel = Events

        # return any errors if found
        return self.cleaned_data
        

def index(request):
    return render(request, "sports/index.html")

@csrf_exempt
def update(request, id):

    # Query for requested event
    try:
        event = Events.objects.get(pk=id)
        attending = event.attendees.all()
    except Events.DoesNotExist:
        return JsonResponse({"error": "Event not found."}, status=404)

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("attendees") is not None:
            user = data["attendees"]
            try:
                user = User.objects.get(username=user)
                # If user is attending, remove them
                if user in attending:
                    event.attendees.remove(user)
                    # Increase number attending by 1
                    if data.get("number_attending") is not None:
                        event.number_attending -= 1
                # Else add user to event
                else:
                    event.attendees.add(user)
                    # Reduce number attending by 1
                    if data.get("number_attending") is not None:
                        event.number_attending += 1
                
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=404)
                
        event.save()
        print("Save was successful")
        return HttpResponse(status=204)
    
    # Method must be via PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def delete(request, id):
    # Query for requested event
    try:
        obj = Events.objects.get(pk=id)
        obj.delete()
        return JsonResponse({"status": "Object deleted successfully"})
    except Events.DoesNotExist:
        return JsonResponse({"status": "Object not found"}, status=404)



# Testing this decorator
#@login_required
def event(request, event_id):
    # Query for requested event
    try:
        event = Events.objects.get(pk=event_id)
    except Events.DoesNotExist:
        return JsonResponse({"error": "Event not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(event.serialize())


def events(request):
    user = request.user

    # Query for events
    try:
        now = datetime.now(pytz.timezone('US/Pacific'))

        # Grab current or upcoming event filtered by day and time
        events = Events.objects.filter(timestamp__gte=now)
      
    except Events.DoesNotExist:
        return JsonResponse({"error": "No events were found."}, status=404)

    #serialize into json
    return JsonResponse([event.serialize() for event in events],safe=False)

def past(request):
    # Query for events
    try:
        now = datetime.now(pytz.timezone('US/Pacific'))
        # Grab past events filtered by day and time
        past_events = Events.objects.filter(timestamp__lte=now)        
      
    except Events.DoesNotExist:
        return JsonResponse({"error": "No events were found."}, status=404)

    #serialize into json
    return JsonResponse([event.serialize() for event in past_events],safe=False)


@login_required(login_url='/login') #redirect when user is not logged in
def create_event(request):
    user = request.user
    if request.method == "POST":
	    
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            
            user = request.user

            # combining to make a datetime instance
            date = form.cleaned_data['date']
            end = form.cleaned_data['end']
            event_end = datetime.combine(date, end)
            now = datetime.now(pytz.timezone('US/Pacific'))
            
            timezone = pytz.timezone('US/Pacific')
            dt_obj = timezone.localize(event_end)
          
            print('Form is valid')
            post = form.save(commit = False) 
            post.host = user
            post.timestamp = dt_obj
           
            post.save()
            id_ = post.id

            # creating an instance with event
            event = Events.objects.get(id=id_)
            # add event to the user
            event.attendees.add(user) 
            event.save() 
            
            return HttpResponseRedirect(reverse("index"))
        else:
            print('Form not valid')
            return render(request, "sports/create_event.html", {
                "form":form
            })
    
    # GET method
    else:
        date_obj = datetime.now(pytz.timezone('US/Pacific'))
        today = date_obj.date()
        today = today + timedelta(days=1)
        initial = {
            'host':user,
            'date':today,
        }
        print(today)
        return render(request, "sports/create_event.html", {
            "form": EventForm(initial=initial)
        })

def password_reset_sent(request):
   
    if request.method == "POST":
        print('Test was ran')
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    print("user:", user)
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password_reset_email.txt"
                    c = {
                    "email":user.email,
                    'domain':'127.0.0.1:8000', #'your-website-name.com',
                    'site_name': 'Website Name',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, env('USER_EMAIL'), [user.email], fail_silently=False)
                    
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                        
                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                    return HttpResponseRedirect(reverse("index"))
            #else:
            #    messages.success(request, 'An invalid email has been entered.')
    form = PasswordResetForm()
    return render(request, "registration/password_reset_done.html", {
        "form":form
        })

def password_reset_request(request):
	if request.method == "POST":
		form = PasswordResetForm(request.POST)
		if form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "registration/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'your-website-name.com',
					'site_name': 'Website Name',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': 'https',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'christian7art@yahoo.com', [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
						
					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return HttpResponseRedirect(reverse("index"))
			messages.error(request, 'An invalid email has been entered.')
	form = PasswordResetForm()
	return render(request, "registration/password_reset.html", {
        "form":form
        })


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse("index"))
        else:
            # Return an 'invalid login' error message.
            messages.success(request, ("There was an error logging in, try again."))
            return redirect('login')
    else:
        return render(request, "sports/login.html")


def logout_user(request):
    logout(request)
    messages.success(request, ("You Were Logged Out!"))
    # for now I'll redirect to index
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        
        # Grab the values from the form
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Check passwords match, else raise message
        if password != confirmation:
            return render(request, "sports/register.html", {
                "message": "Passwords must match."
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        # Database field null = false, expects a value
        except IntegrityError:
            return render(request, "sports/register.html", {
                "message": "Username already taken."
            })

        # Calls the login function with user's credentials
        # Do I need to authenicate the user?
        login(request, user)
        messages.success(request, ("Registration Successful!"))
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "sports/register.html")

    
