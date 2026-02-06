from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404
from django.dispatch import receiver

def category_icon_upload_path(instance, filename):
    return f"category/{instance.id}/category_icon/{filename}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.FileField(upload_to=category_icon_upload_path, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if self.id:
            existing  = get_object_or_404(Category, id=self.id)
            if existing.icon != self.icon:
                existing.icon.delete(save=False)
            super(Category, self).save(*args, **kwargs)

    @receiver()

    def __str__(self):
        return self.name


class Server(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="server_owner")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="server_category")
    description = models.CharField(max_length=500, blank=True, null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)
    #banner = 
    #icon =

    def __str__(self):
        return f"{self.name}-{self.id}"

class Channel(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="channel_owner")
    topic  = models.CharField(max_length=100)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="channel_server")

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Channel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    


