document.onkeyup = enter;    
function enter(e) {if (e.which == 13) emptycheck();}

function validate() {
    var txt;
    if (confirm("Confirm Logout?")) {
      window.location.href="Login.html";
    }
  }

  function emptycheck(){
    var ipt = document.getElementById('message-input').value;

    if (ipt==""){
    }
    else{
      sendMessage();
    }
  }

  function report(){
    var query = document.getElementById("message-input").value;
    alert("We have created an error report to alert the developers to add a response to the prompt : " + query);
  }

  function link(){
    var anchor = document.createElement('a');
    var link = document.createTextNode("https://www.google.com");
    anchor.appendChild(link);
    anchor.href = "https://www.google.com";
    anchor.style.color="white";
    anchor.style.padding = "5px";
    anchor.style.marginTop = "5px";
    anchor.style.maxWidth = "75px";
    anchor.style.display = "inline-block";
    document.getElementById("chat-body").appendChild(anchor);
  }

  function sendMessage() {
    var query = document.getElementById("message-input").value;
    if (query.trim() === '') return; // Don't send empty messages

    displayUserMessage(query);
    sendToServer(query);
}

function displayUserMessage(message) {
    var div = document.createElement("div");
    var p = document.createElement("p");
    p.style.background = "white";
    p.style.color = "black";
    p.style.padding = "10px";
    p.style.borderRadius = "5px";
    p.style.display = "inline-block";
    p.style.maxWidth = "60%";
    p.innerHTML = message;
    div.appendChild(p);
    document.getElementById("chat-body").appendChild(div);
    document.getElementById("message-input").value = ""; // Clear input field
}

function displayServerResponse(message) {
    var div = document.createElement("div");
    var p = document.createElement("p");
    p.style.background = "#2a2a2a";
    p.style.color = "white";
    p.style.padding = "10px";
    p.style.borderRadius = "5px";
    p.style.display = "inline-block";
    p.style.maxWidth = "75%";
    p.innerHTML = message;
    div.appendChild(p);
    document.getElementById("chat-body").appendChild(div);
}

function sendToServer(query) {
  var form = new FormData();
  var assistantId = document.getElementById("assistant-id-input").value;
  var threadId = document.getElementById("thread-id-input").value;

  form.append("assistant_ID", assistantId);
  form.append("message", query);
  if (threadId.trim() !== '') {
      form.append("thread_id", threadId);
  }

  var settings = {
      "url": "http://127.0.0.1:8000/api/v1/core/chat_hotel/",
      "method": "POST",
      "timeout": 0,
      "headers": {
          "Authorization": "Bearer [Your_Token_Here]"
      },
      "processData": false,
      "mimeType": "multipart/form-data",
      "contentType": false,
      "data": form
  };

  $.ajax(settings).done(function (response) {
      displayServerResponse(response);
  });
}
