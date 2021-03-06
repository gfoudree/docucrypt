from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Upload

from .backend.upload import *
import website.models

import base64

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html', {'title' : 'Docucrypt'})

def upload(request):
    if request.method == 'POST':
        fileParam = request.POST.get('data', '').encode()
        IVParam = request.POST.get('IV', '').encode()

        encryptedFile = b''
        IV = b''

        # Check the passed parameters for validity
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

def viewFile(request, fileID, decryptionKey):
     return render(request, 'viewfile.html', {'data' : ''})

def manage(request, fileID, decryptionKey):
    pass

# Retrieves a file given the UUID from the database and sends the ciphertext back
def download(request):
    fileID = request.POST.get('id', '')
    if len(fileID) != website.models.FILE_UUID_LENGTH:
        print("Invalid request to download file of UUID {} as length ({}) != {}".format(fileID, len(fileID), website.models.FILE_UUID_LENGTH))
        return JsonResponse({'success': False, 'error': 'Invalid file name'}, status=400)
    try:
        upload = Upload.objects.get(fileUUID=fileID)
        fileData = base64.b64encode(open(upload.uploadedToFile, 'rb').read()).decode()

        return JsonResponse({'success': True, 'cipherText': fileData, 'salt': upload.salt, 'IV': upload.IV})
    except Exception as err:
        print("Error reading encrypted upload file " + str(err))
        return JsonResponse({'success': False, 'error': 'Invalid file name'}, status=400)
