from __future__ import unicode_literals
from django.db import models
from datetime import datetime, timedelta
import bcrypt, re

class UserManager(models.Manager):
    def validate(self, postData):
        errors = []
        if len(postData['first_name']) == 0:
            errors.append('Please Enter First Name.')
        elif len(postData['first_name']) < 2:
            errors.append('First Name must be between 3-45 characters')
        elif not re.search(r'^[A-Za-z]+$', postData['first_name']):
            errors.append('First name must only contain letters')
        if len(postData['alias']) == 0:
            errors.append('Please Enter a Alias.')
        elif len(postData['alias']) < 2:
            errors.append('Alias must be between 3-45 characters')
        elif not re.search(r'^[A-Za-z]+$', postData['alias']):
            errors.append('Alias must only contain letters')
        if len(postData['email']) == 0:
            errors.append('Email cannot be left blank')
        elif not re.search(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$',postData['email']):
            errors.append('You have entered an invalid Email')
        elif len(User.objects.filter(email=postData['email']))>0:
            errors.append('This email is already registered')
        if len(postData['password']) < 7:
            errors.append('Password must be at least 8 characters')
        if postData['confirm'] != postData['password']:
            errors.append('Password and confirm password does not match')
        try:
            dob = datetime.strptime(postData['dob'], '%m/%d/%Y')
            if datetime.now() < dob:
                errors.append('DOB cannot be in the future')
        except ValueError:
            errors.append('Invalid date entry, must be mm/dd/yyyy')
        if len(errors)== 0:
            user = User.objects.create(first_name=postData['first_name'], alias= postData['alias'], email=postData['email'],dob=dob, pw_hash=bcrypt.hashpw(postData['password'].encode(),bcrypt.gensalt()))
            return (True, user)
        return(False, errors)

    def authenticate(self, postData):
        if 'email' in postData and 'password' in postData:
            try:
                user = User.objects.get(email=postData['email'])
            except User.DoesNotExist:
                return(False, 'Invalid email, or password does not match email')
            u = user.pw_hash.encode()
            if bcrypt.hashpw(postData['password'].encode(),u)== u:
                return (True, user)
            else:
                return (False, 'Email and password combination do not match')
        else:
            return (false, 'Please enter Login information')

class User(models.Model):
    first_name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    dob = models.DateTimeField()
    pw_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()


class Poke(models.Model):
    poker = models.ForeignKey(User, related_name="pokerpokes")
    poked = models.ForeignKey(User, related_name="pokedpokes")
    created_at = models.DateField(null=True)
    counter = models.IntegerField(blank=False, default=0, null=True)
