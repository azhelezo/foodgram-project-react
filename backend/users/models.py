from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FollowUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='follow_unique')
        ]

    def __str__(self):
        return f'{self.user} follows {self.author}'
