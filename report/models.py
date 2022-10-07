from django.db import models
from django.utils import timezone


# Create your models here.
class Twitter_user(models.Model):

    user_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.user_name


class Twitter_user_stats(models.Model):

    user_id = models.ForeignKey(Twitter_user, on_delete=models.CASCADE)
    tweets = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('timestamp', 'user_id')

    def __str__(self):
        return self.followers
