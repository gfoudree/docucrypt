function sendMessage(message, severity) {
    console.log(message);
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
        {"name": "AES-CBC",
         iv
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
       let salt = window.crypto.getRandomValues(new Uint8Array(16));
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
           {"name": "AES-CBC"},
           true,
           ["encrypt", "decrypt"]
       );

       console.log("key=" + base64js.fromByteArray(scryptKey));
       console.log("iv=" + base64js.fromByteArray(iv));
       console.log("salt=" +salt);
    }

    let cipherText = window.crypto.subtle.encrypt(
        {"name": "AES-CBC",
         iv
        },
        key,
        enc.encode(data)
    );
    let exportedKey = await crypto.subtle.exportKey("raw", key);
    exportedKey = new Uint8Array(exportedKey);

    return {'IV': iv, 'CipherText': await cipherText, 'Key': exportedKey};
}

function handleUpload() {
    var file = document.getElementById('fileToUpload').files[0];

    if (file.size > (25 * 1024 * 1024)) { // Check if file size is within 25MB limit
        sendMessage("Size is greater than 25MB!", "error");
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
        let password = $('#passwordField').val();
        if (password) {
            if (password.length < 8) {
                sendMessage('Password length is too short. Please use more than 8 characters!', 'error');
                return;
            }

            encryptData(fReader.result, password).then(function(encryptedDocument) {
                console.log(encryptedDocument);
            });
        }
        else {
            encryptData(fReader.result, '').then(function(encryptedDocument) {
                console.log(encryptedDocument);
            });
        }
    }

    fReader.onerror = function () {
        sendMessage("Error uploading file", "critical");
    }

    fReader.readAsBinaryString(file);
}