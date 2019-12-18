from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Upload

import secrets
import base64
import hashlib
import datetime
from datetime import *

UPLOAD_FOLDER = '/tmp/'
EXPIRATION_TABLE = [timedelta(hours=12), timedelta(days=1), timedelta(days=7),
        timedelta(days=28), timedelta(days=365)]

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html', {'title' : 'Docucrypt'})

def saveUploadedFile(request):
    # Get parameters
    fileName = request.POST.get('fileName', '')
    expirationTime = int(request.POST.get('expirationTime', '5'))
    fileParam = request.POST.get('data', '').encode()
    IVParam = request.POST.get('IV', '').encode()
    salt = request.POST.get('Salt', '')

    # Save file to disk
    fileData = base64.decodebytes(fileParam)
    fName = "{0}{1}.upload".format(UPLOAD_FOLDER, secrets.token_hex(32))
    urlFName = secrets.token_urlsafe(40)[:40] # Name for url portion (http://swag.com/get/urlFName#decryptionKey), truncated @ 40 b/c param is bits -> var output len

    writtenBytes = 0

    with open(fName, 'wb') as f:
        writtenBytes = f.write(fileData)
    
    # Calculate Checksum
    hsh = hashlib.sha256()
    hsh.update(fileData)

    # Populate model & save
    try:
        upload = Upload()
        upload.uploadTime = datetime.datetime.now()
        upload.fileName = fileName
        upload.urlFName = urlFName
        upload.IV = IVParam.decode()
        upload.salt = salt
        upload.uploadedToFile = fName
        upload.fileSize = writtenBytes
        if expirationTime == 5:
            upload.expirationTime = -1
        else:
            upload.expirationTime = upload.uploadTime + EXPIRATION_TABLE[upload.expirationTime]
        upload.fileSHA256 = hsh.hexdigest()
        upload.save()
        print(upload)
        return {'success': True, 'url': urlFName}
    except:
        return {'success': False, 'url': ''}

def upload(request):
    if request.method == 'POST':
        fileParam = request.POST.get('data', '').encode()
        IVParam = request.POST.get('IV', '').encode()

        encryptedFile = b''
        IV = b''

        # Check the passed parameters
        if len(IVParam) < 5 or len(fileParam) < 5:
            return HttpResponse("Bad upload", status=400)
        try: # Try to decode, abort if it is broken
            IV = base64.decodebytes(IVParam)
            encryptedFile = base64.decodebytes(fileParam)
        except:
            return HttpResponse("Bad upload", status=400)
        
        if len(IV) != 16: # IV is truncated?
            return HttpResponse("Bad upload", status=400)
        
        result = saveUploadedFile(request)
        if result['success']:
            return JsonResponse(result)
        else:
            return HttpResponse(result, status=400)
    else:
        return redirect('/')

def getFile(request, fileID):
    if len(fileID) != 40:
        return HttpResponse("Bad file name", status=400)
    try:
        upload = Upload.objects.get(urlFName=fileID)
        return HttpResponse("Found!")
    except:
        return HttpResponse("Bad file name", status=400)
