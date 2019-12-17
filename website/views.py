from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Upload

import secrets
import base64
import hashlib
import datetime

UPLOAD_FOLDER = '/tmp/'
EXPIRATION_TABLE = ['12 Hours', '24 Hours', '1 Week', '1 Month', '1 Year', 'Never']

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html', {'title' : 'Docucrypt'})

def saveUploadedFile(request):
    # Get parameters
    fileName = request.POST.get('fileName', '')
    expirationTime = int(request.POST.get('expirationTime', '5'))
    fileParam = request.POST.get('data', '').encode()
    IVParam = request.POST.get('IV', '').encode()

    # Save file to disk
    fileData = base64.decodebytes(fileParam)
    fName = "{0}{1}.upload".format(UPLOAD_FOLDER, secrets.token_hex(32))
    urlFName = secrets.token_urlsafe(32) # Name for url portion (http://swag.com/get/urlFName#decryptionKey)

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
        upload.uploadedToFile = fName
        upload.fileSize = writtenBytes
        upload.expirationTime = EXPIRATION_TABLE[expirationTime] #TODO: change this to use current time + expiration time so we can cronjob cleanup!
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