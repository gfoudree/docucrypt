from django.db import models
from datetime import datetime

class Upload(models.Model):
    uploadTime = models.DateTimeField(auto_now_add=True)
    fileName = models.CharField(max_length=200)
    fileSHA256 = models.CharField(max_length=128)
    uploadedToFile = models.CharField(max_length=200)
    IV = models.CharField(max_length=32)
    fileSize = models.IntegerField()
    expirationTime = models.CharField(max_length=10)

    def __str__(self):
        return '{} {} {} {} {} {} {}'.format(self.uploadTime, self.fileName,
            self.fileSHA256, self.uploadedToFile, self.IV, self.fileSize,
            self.expirationTime)