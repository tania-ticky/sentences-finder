from django.db import models

class Topic(models.Model):
    top_name = models.CharField(max_length=264,unique=True)

    def __str__(self):
        return self.top_name

class Webpage(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE,)
    name = models.CharField(max_length=264,unique=True)
    url = models.URLField(unique=True)

    def __str__(self):
        return self.name

class AccessRecord(models.Model):
    name = models.ForeignKey(Webpage, on_delete=models.CASCADE,)
    date = models.DateField()

    def __str__(self):
        return str(self.date)

class User(models.Model) :
    sentences_finder_name = models.CharField(max_length=264)
    Last_name = models.CharField(max_length=264)
    Email = models.EmailField(max_length=264, unique = True)
    def __str__(self):
            return self.sentences_finder_name
