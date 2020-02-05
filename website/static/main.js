$(document).ready(function () {
    $('.ui.dropdown').dropdown(); // Initialize dropdown library for menu

    var uploadDiv = $('#uploadBox');
    var fileInput = uploadDiv.find('input[type=file]');
    var label = $('#uploadLabel');
    uploadDiv.on('drag dragstart dragend dragover dragenter dragleave drop', function (e) {
        e.preventDefault();
        e.stopPropagation();
    })
        .on('dragover dragenter', function () {
            uploadDiv.addClass('upload-dragover');
        })
        .on('dragleave dragend drop', function () {
            uploadDiv.removeClass('upload-dragover');
        })
        .on('drop', function (e) {
            droppedFiles = e.originalEvent.dataTransfer.files;
            label.text(droppedFiles[0].name);
            fileInput.files = droppedFiles[0];
        });
    fileInput.on('change', function (e) {
        label.text(e.target.files[0].name);
    });
});

function checkPassword() {
    var pass = $('#passwordInputField').val();
    if ((pass.length < 8 && pass.length > 0) || (pass.length > 64)) { // Must be at least 8 chars and less than 64
        $('#passwordField').addClass('error');
        $('#passwordField').popup({
            content : 'Password must be between 8-64 characters',
            position: 'left center',
        });
        $('#passwordField').popup('show');
    }
    else {
        $('#passwordField').removeClass('error');
        $('#passwordField').popup('destroy');
    }
}

// TODO: Change this to be a hidden div in the page and just update the content
function displayMessage(message, title, bad) {
    var html = '<div class="ui ';
    if (bad) {
        html += 'negative';
    }
    else {
        html += 'positive';
    }
    html += ' message" id="message"> \
        <i class="close icon" onclick="deleteMessage()"></i> \
        <div class="header">' + title + '\n</div>\n<p>\n' + message + '\</p>\n</div>';

    $(html).hide().fadeIn(500).insertAfter("#form");
    $('.message .close').on('click', function () {
        $(this)
            .closest('.message')
            .transition('fade');
    });
}

function sendMessage(message, severity) {
    console.log(message);
}

async function decrypt(b64CipherText, b64IV, b64UrlKey) {
    let cipherText =  base64js.toByteArray(b64CipherText);
    let key = Base64DecodeUrl(b64UrlKey);
    let IV = base64js.toByteArray(b64IV);

    let importedKey = await crypto.subtle.importKey(
        "raw",
        key,
        "AES-CBC",
        false,
        ["decrypt"]
    );

    let plainText = await window.crypto.subtle.decrypt(
        {
            name: "AES-CBC",
            iv: IV
        },
        importedKey,
        cipherText.buffer
    );
    
    let dec = new TextDecoder();
    return dec.decode(plainText);
}

async function encrypt(data) {
    let enc = new TextEncoder();
    let aesKey = await window.crypto.subtle.generateKey(
        {
            name: "AES-CBC",
            length: 256
        },
        true,
        ["encrypt", "decrypt"]
    );
    let iv = window.crypto.getRandomValues(new Uint8Array(16));

    let cipherText = await window.crypto.subtle.encrypt(
        {
            name: "AES-CBC",
            iv: iv
        },
        aesKey,
        enc.encode(data)
    );

    return cipherText;
}

async function encryptData(data, password) {
    let enc = new TextEncoder();
    let iv = window.crypto.getRandomValues(new Uint8Array(16));
    let key;
    let salt;

    if (password.length === 0) {
        // Generate random AES key
        key = await window.crypto.subtle.generateKey(
            {
                name: "AES-CBC",
                length: 256
            },
            true,
            ["encrypt", "decrypt"]
        );
    }
    else {
        // Derive AES key from password
        salt = window.crypto.getRandomValues(new Uint8Array(16));
        salt = base64js.fromByteArray(salt);
        scryptKey = await scrypt.async(
            password,
            salt,
            16384,
            8,
            1,
            32,
            undefined,
            300
        );
        key = await crypto.subtle.importKey(
            "raw",
            scryptKey,
            { name: "AES-CBC" },
            true,
            ["encrypt", "decrypt"]
        );

        console.log("key=" + base64js.fromByteArray(scryptKey));
        console.log("iv=" + base64js.fromByteArray(iv));
        console.log("salt=" + salt);
    }

    let cipherText = window.crypto.subtle.encrypt(
        {
            name: "AES-CBC",
            iv: iv
        },
        key,
        enc.encode(data)
    );
    let exportedKey = await crypto.subtle.exportKey("raw", key);
    exportedKey = new Uint8Array(exportedKey);

    return { 'IV': iv, 'CipherText': await cipherText, 'Key': exportedKey, 'Salt': salt };
}

function handleUpload() {
    var file = document.getElementById('fileToUpload').files[0];
    var uploadButton = document.getElementById('uploadButton');
    uploadButton.classList.add("loading");

    if (file.size > (25 * 1024 * 1024)) { // Check if file size is within 25MB limit
        displayMessage('', "Size is greater than 25MB!", true);
        return;
    }

    var fReader = new FileReader();
    fReader.onprogress = function (progEvent) {
        if (progEvent.lengthComputable) {
            var percentLoaded = Math.round((progEvent.loaded * 100) / progEvent.total);
            console.log("Loaded " + percentLoaded);
        }
    }
    fReader.onloadend = function () {
        // Check if password is supplied
        let password = $('#passwordInputField').val();
        if (password) {
            if (password.length < 8) {
                displayMessage('Password length is too short. Please use more than 8 characters!', true);
                return;
            }

            encryptData(fReader.result, password).then(function (encryptedDocument) {
                console.log(encryptedDocument);
                sendEncryptedContent(encryptedDocument);
            });
        }
        else {
            encryptData(fReader.result, '').then(function (encryptedDocument) {
                console.log(encryptedDocument);
                sendEncryptedContent(encryptedDocument);
            });
        }
    }

    fReader.onerror = function () {
        displayMessage('', "Error uploading file", true);
    }
    fReader.readAsBinaryString(file);
}

function sendEncryptedContent(encryptedDocument) {
    var csrfToken = jQuery("[name=csrfmiddlewaretoken]").val();
    var encBytes = new Uint8Array(encryptedDocument['CipherText']);
    let fd = new FormData();
    let encryptionKey = encryptedDocument['Key'];

    fd.append('data', base64js.fromByteArray(encBytes));
    fd.append('IV', base64js.fromByteArray(encryptedDocument['IV']));
    fd.append('Salt', encryptedDocument['Salt']);
    fd.append('expirationTime', $('#expirationTime').val());
    fd.append('fileName', document.getElementById('fileToUpload').files.item(0).name);

    $.ajax({
        type: 'POST',
        url: '/upload/',
        data: fd,
        headers: { 'X-CSRFToken': csrfToken },
        processData: false,
        contentType: false,
        error: function (request, error) {
            displayMessage('', "Error sending encrypted file to server!", true);
        },
        success: function (data) {
            displayMessage('', 'File upload success!', false);
            console.log(data);
            
            // Compute URL to retrieve file with format /fileUUID#key
            var fileUrl = window.location.protocol + "//" + window.location.hostname;
            if (window.location.port.length > 0 ) { //Are we running on a non-standard port? (debugging)
                fileUrl += ":" + window.location.port;
            }
            fileUrl += "/viewFile/" + data['url'] + "/" + Base64EncodeUrl(encryptionKey);
            console.log("URL: " + fileUrl);

        }
    });
    var uploadButton = document.getElementById('uploadButton');
    uploadButton.classList.remove("loading");
}

function Base64DecodeUrl(str){
    while ((str.length % 4) != 0) { //Add padding if necessary
        str += "=";
    }
    return base64js.toByteArray(str.replace(/-/g, '+').replace(/_/g, '/'));
}

function Base64EncodeUrl(str){
    var b64 = base64js.fromByteArray(str);
    return b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
}

function getEncryptedFile() {
    let csrfToken = jQuery("[name=csrfmiddlewaretoken]").val();
    let fileUUID = window.location.pathname.split('/')[2]; // UUID of file to fetch
    let decryptionKey = window.location.pathname.split('/')[3]; // Decryption key
    $.ajax({
        type: 'POST', 
        url:'http://127.0.0.1:8000/download/', 
        headers:{'X-CSRFToken': csrfToken}, 
        data:{'id': fileUUID},
        success: (data, status) => {
            console.log(data);
            decrypt(data['cipherText'], data['IV'], decryptionKey).then(decryptedData => {
                console.log(decryptedData);
            });

        },
        error: (request, status, error) => {
            console.log('Error');
        }
    });
}