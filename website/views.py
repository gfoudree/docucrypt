from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

import base64
# Create your views here.

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html', {'title' : 'Docucrypt'})

def upload(request):
    if request.method == 'POST':
        fileParam = request.POST.get('data', '').encode()
        IVParam = request.POST.get('IV', '').encode()

        encryptedFile = b''
        IV = b''

        if len(IVParam) < 5 or len(fileParam) < 5:
            return HttpResponse("Bad upload", status=400)
        try: # Try to decode, abort if it is broken
            IV = base64.decodebytes(IVParam)
            encryptedFile = base64.decodebytes(fileParam)
        except:
            return HttpResponse("Bad upload", status=400)
        
        if len(IV) != 16: # IV is truncated?
            return HttpResponse("Bad upload", status=400)
        
        print("IV = {}".format(IV))
        return HttpResponse("OK")
    else:
        return redirect('/')