from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass
    
    def __str__(self):
       return f"{self.username}"
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            }

SPORTS = (
    ("soccer", "Soccer"),
    ("baseball", "Baseball"),
    ("basketball", "Basketball"),
    ("football", "Football"),
    ("tennis", "Tennis"),
    ("volleyball", "Volleyball"),
    ("softball", "Softball"),
    ("golf", "Golf"),
    ("ultimate frisbee", "Ultimate Frisbee"),
    ("cycling", "Cycling"),
    ("chess", "Chess"),
    ("other", "Other")
)

class Events(models.Model):
    title = models.CharField(max_length=64, null=False, blank=False)
    description = models.TextField(max_length=250, null=False, blank=False)
    host = models.ForeignKey("User", on_delete=models.CASCADE)
    attendees = models.ManyToManyField("User", related_name="attending", blank=True)
    date = models.DateField(blank=False)
    start = models.TimeField(blank=False)
    end = models.TimeField(blank=False)
    timestamp = models.DateTimeField(blank=True)
    category = models.CharField(max_length=64,choices=SPORTS, null=False, blank=False)
    number_attending = models.IntegerField()
    location = models.CharField(max_length=64)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    
    def __str__(self):
            return f"{self.id}{self.title}{self.description}{self.host}{self.date}{self.start}{self.end}{self.timestamp}{self.category}{self.description}{self.number_attending}{self.location}{self.image}"

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "host": self.host.username,
            "attendees": [user.username for user in self.attendees.all()],
            "date": self.date.strftime("%m-%d-%Y"),
            "start": self.start.strftime("%I:%M %p"),
            "end": self.end.strftime("%I:%M %p"),
            "category": self.category.capitalize(),
            "number_attending": self.number_attending,
            "location": self.location,
            "image":str(self.image)
        }
    
    class Meta:
            # Orders events in reverse date order
            ordering = ['-date']



