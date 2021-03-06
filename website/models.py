from django.db import models
from datetime import datetime

FILE_UUID_LENGTH = 46

class Upload(models.Model):
    uploadTime = models.DateTimeField(auto_now_add=True)
    fileName = models.CharField(max_length=200)
    fileSHA256 = models.CharField(max_length=128)
    uploadedToFile = models.CharField(max_length=200)
    IV = models.CharField(max_length=32)
    fileSize = models.IntegerField()
    expirationTime = models.CharField(max_length=10)
    fileUUID = models.CharField(max_length=64)
    salt = models.CharField(max_length=128)

    def __str__(self):
        urlToFile = "http://127.0.0.1:8000/getFile/{}".format(self.fileUUID)
        return 'Time:{} Name:{} Hash:{} LocalFile:{} IV:{} Size:{} Expires:{} URL:{}'.format(self.uploadTime, self.fileName,
            self.fileSHA256, self.uploadedToFile, self.IV, self.fileSize,
            self.expirationTime, urlToFile)