from django.db import models
from django.contrib import admin

# Create your models here.
class Story(models.Model):
    """A story"""
    
    headline = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    subhead = models.CharField(blank=True, max_length=255)
    byline = models.CharField(max_length=255)
    story = models.TextField(blank=True)

    def __unicode__(self):
        return self.headline

class StoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'byline',)
    prepopulated_fields = {'slug': ('headline',)}
    
admin.site.register(Story, StoryAdmin)