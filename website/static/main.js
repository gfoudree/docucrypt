var ciphertext = CryptoJS.AES.encrypt('my message', 'secret key 123');
var bcrypt = dcodeIO.bcrypt;
var salt = bcrypt.genSaltSync(10);

function sendMessage(message, severity) {
    console.log(message);
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
        console.log(fReader.result);
    }
    fReader.onerror = function () {
        sendMessage("Error uploading file", "critical");
    }

    fReader.readAsBinaryString(file);
}