from django.db import models


class Restaurant(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class FacebookPost(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    publish_date = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
