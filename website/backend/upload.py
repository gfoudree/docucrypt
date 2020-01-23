import secrets
import base64
import hashlib
import os
import datetime
from datetime import *

from website.models import Upload

UPLOAD_FOLDER = '/tmp/'
EXPIRATION_TABLE = [timedelta(hours=12), timedelta(days=1), timedelta(days=7),
        timedelta(days=28), timedelta(days=365)]

def saveUploadedFile(request):
    # Get parameters
    fileName = request.POST.get('fileName', '')
    expirationTime = 5 if request.POST.get('expirationTime', '5') == '' else int(request.POST.get('expirationTime', '5'))
    fileParam = request.POST.get('data', '').encode()
    IVParam = request.POST.get('IV', '').encode()
    salt = request.POST.get('Salt', '')

    # Save file to disk
    fileData = base64.decodebytes(fileParam)
    fName = "{0}{1}.upload".format(UPLOAD_FOLDER, secrets.token_hex(32)) # Separate file name for local file for security
    fileUUID = secrets.token_urlsafe(46)[:46] # Name for url portion (http://swag.com/get/fileUUID#decryptionKey), truncated @ 46 b/c param is bits -> var output len

    writtenBytes = 0
    with open(fName, 'wb') as f:
        writtenBytes = f.write(fileData)
    
    # Calculate Checksum
    hsh = hashlib.sha256()
    hsh.update(fileData)

    # Populate model & save
    try:
        upload = Upload()
        upload.uploadTime = datetime.now()
        upload.fileName = fileName
        upload.fileUUID = fileUUID
        upload.IV = IVParam.decode()
        upload.salt = salt
        upload.uploadedToFile = fName
        upload.fileSize = writtenBytes

        upload.expirationTime = -1 if expirationTime == 5 else expirationTime
        upload.expirationTime = upload.uploadTime + EXPIRATION_TABLE[upload.expirationTime] # Compute expiration time with timedelta

        upload.fileSHA256 = hsh.hexdigest()
        upload.save()
        print(upload)
        return {'success': True, 'url': fileUUID}
    except Exception as err:
        print("Error saving uploaded file to database: " + str(err))
        return {'success': False, 'url': ''}