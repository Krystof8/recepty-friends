from django.db import models

# Create your models here.
class ProfilePictureModel(models.Model):
    username = models.CharField(
        blank=True,
        null=False
    )
    image = models.ImageField(
        upload_to='profile_pictures/',
        blank=False,
        null=True
    )

    def __str__(self):
        return self.username + ' - profilový obrázek'
    

class FriendsRequestModel(models.Model):
    request_sender = models.CharField()

    request_receiver = models.CharField()

    def __str__(self):
        return self.request_sender + ' → ' + self.request_receiver
    

class FriendListModel(models.Model):
    profile = models.CharField()

    friend = models.CharField()

    def __str__(self):
        return self.profile + ' → ' + self.friend
    


# mdoel na pridavani receptu
class ReceptModel(models.Model):
    title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        unique=True
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    ingredients = models.TextField(
        blank=False,
        null=False
    )
    image = models.ImageField(
        upload_to='receipt_images/',
        blank=True,
        null=True
    )
    user_id = models.IntegerField(
        blank=True,
        null=True
    )


class Ingredients(models.Model):
    name = models.CharField(max_length=50, unique=True)
    user_id = models.IntegerField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name