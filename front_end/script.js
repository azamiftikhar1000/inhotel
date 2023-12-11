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

  function sendMessage(){
      var query = document.getElementById("message-input").value;
      var div = document.createElement("div");
      var p = document.createElement("p");
      p.style.background = "white";
      p.style.color = "black";
      p.style.padding = "10px";
      p.style.borderRadius = "5px";
      p.style.display = "inline-block";
      p.style.maxWidth = "60%";
      p.innerHTML = query;
      document.getElementById("chat-body").appendChild(div);
      document.getElementById("chat-body").appendChild(p);
      response();
    }

  function response(){
      var empty = false;
      var query = document.getElementById("message-input").value;
      var input = query.toLowerCase();
      var div = document.createElement("div");
      var p = document.createElement("p");
      p.style.background = "#2a2a2a";
      p.style.color = "white";
      p.style.padding = "10px";
      p.style.borderRadius = "5px";
      p.style.display = "inline-block";
      p.style.margin = "0";
      p.style.maxWidth = "75%";
      document.getElementById("chat-body").appendChild(div);
      document.getElementById("chat-body").appendChild(p);

      //Chatbot logic

      p.innerHTML = "azam is a bot";

      document.getElementById("message-input").value = "";
    }
