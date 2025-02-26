var uri = "https://localhost:8003/mfs100/"; // Mantra MFS100 SDK API

function CaptureFingerprint() {
    console.log("Fingerprint capture started...");

    var request = { "Quality": 60, "TimeOut": 10000 };
    var jsondata = JSON.stringify(request);

    fetch(uri + "capture", {
        method: "POST",
        body: jsondata,
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response from MFS100:", data);

        if (data.ErrorCode == "0") {
            let base64Image = data.BitmapData;
            document.getElementById("fingerprint-image").src = "data:image/png;base64," + base64Image;
            console.log("Sending fingerprint to Flask...");

            // Automatically send to Flask
            sendToFlask(base64Image);
        } else {
            document.getElementById("result").innerText = "Capture failed: " + data.ErrorDescription;
        }
    })
    .catch(error => console.log("Error:", error));
}

function sendToFlask(base64Image) {
    fetch("/predict", {
        method: "POST",
        body: JSON.stringify({ "image": base64Image }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        console.log("Raw response:", response);
        if (!response.ok) {
            return response.text().then(text => { throw new Error("Flask returned: " + text); });
        }
        return response.json();
    })
    .then(data => {
        console.log("Response from Flask:", data);
        document.getElementById("result").innerText = "Predicted Blood Group: " + data.blood_group;
    })
    .catch(error => {
        console.log("Error sending to Flask:", error);
        document.getElementById("result").innerText = "Error: " + error.message;
    });
}



 // Fetch the logged-in user and update UI dynamically
 function fetchUser() {
    fetch('/user')
    .then(response => {
        if (!response.ok) {
            throw new Error("Not logged in");
        }
        return response.json();
    })
    .then(data => {
        document.getElementById("username").textContent = "";
        document.getElementById("logout-btn").style.display = "inline-block";
    })
    .catch(error => {
        console.log("User not logged in:", error);
        document.getElementById("username").innerHTML = 'Please <a href="/login">login</a> to continue.';
    });
}

// Logout function
document.getElementById("logout-btn").addEventListener("click", function() {
    window.location.href = "/logout";
});

// Call fetchUser on page load
fetchUser();



// function fetchUser() {
//     fetch('/user')
//     .then(response => response.json())
//     .then(data => {
//         if (data.username) {
//             document.getElementById("username").textContent = "Welcome, " + data.username;
//             document.getElementById("logout-btn").style.display = "inline-block";
//         }
//     })
//     .catch(error => console.log("Error fetching user:", error));

// document.getElementById("logout-btn").addEventListener("click", function() {
//     window.location.href = "/logout";
// })
// fetchUser();
// }
