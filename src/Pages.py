def stylesheet(state):
    html = """
body {
    width:100%;
    margin:0 auto;
}
#header {
    width: 100%;
    margin:0 auto;
    background-color: lightblue;
}
#header h1,#NavBar {
    width: 720px;
    margin:0 auto;
}
#header h1 {
    padding: 10px;
}
#main {
    width: 720px;
    margin:0 auto;
}

@media screen and (max-width: 500px) {
    #header h1,#NavBar {
        width: 100%;
        padding: 0px;
    }
    #main {
        width: 100%;
    }
}

#NavBar a, #NavBar span {
    padding-left: 10px;
    padding-right: 10px;
    text-decoration:none;
}

h1 {
    font-family: sans-serif;
}
a {
    color: black;
    font-family: sans-serif;
}
a:hover, #NavBar span {
    background-color: blue;
    color: white;
}

#action_modes button {
    background-color: lightgreen;
    border: 2px solid greenyellow;
    display: inline-block;
    text-decoration: none;
    border-radius: 5px;
}

#action_modes button.active {
    background-color: green;
    color: white;
    border-color: green;
}

#action_modes button:hover {
    border-color: green;
}

#control_area img {
    width: 30%;
}

#control_area {
    position: relative;
    width: 100%;
    aspect-ratio: 1;
}

#control_area #up_arrow {
    position: absolute;
    left: 35%;
    top: 10%;
}

#control_area #left_arrow {
    transform: rotate(-90deg);
    position: absolute;
    left: 10%;
    top: 50%;
    bottom: 50%;
    margin: auto;
}

#control_area #right_arrow {
    transform: rotate(90deg);
    position: absolute;
    right: 10%;
    top: 50%;
    bottom: 50%;
    margin: auto;
}

#control_area #down_arrow {
    transform: rotate(180deg);
    position: absolute;
    bottom: 10%;
    left: 35%;
}

#control_area #r_right_arrow {
    transform: rotate(135deg);
    position: absolute;
    top: 10%;
    left: 60%;
}

#control_area #r_left_arrow {
    transform: rotate(-135deg);
    position: absolute;
    top: 10%;
    right: 60%;
}

#control_area .pressed
{
    border: 5px solid blue;
    border-radius: 10px;
}

#speed_slider
{
    position: absolute;
    right: 2%;
    height: 100%;
    padding: 0;
}

#speed_slider span
{
    display: block;
    margin-left: auto;
    margin-right: auto;
    padding: 0;
}

#speed_slider div
{
    position: static;
    height: 90%;
    margin-left: auto;
    margin-right: auto;
}

#speed_slider input {
    writing-mode: vertical-lr;
    direction: rtl;
    height: 100%;
    width: 100%;
}

#plane_controls {
    width: 100%;
    aspect-ratio: 1;
    position: absolute;
    top: 100%;
}

#level_button {
    background-color: lightgreen;
    border: 2px solid greenyellow;
    display: inline-block;
    text-decoration: none;
    border-radius: 5px;
}

#plane_range {
    border: 3px solid black;
    border-radius: 100%;
    position: relative;
    top: 5%;
    left: 5%;
    width: 80%;
    height: 80%;
}

#plane_center {
    position: absolute;
    border: 3px solid black;
    border-radius: 100%;
    width: 20%;
    height: 20%;
    top: 40%;
    left: 40%;
}

#plane_point {
    position: relative;
    border: 3px solid black;
    background: green;
    border-radius: 100%;
    width: 20%;
    height: 20%;
    margin: -10%;
    cursor: grab;
    top: 50%;
    left: 50%;
    touch-action: none;
}

#height_slider
{
    position: absolute;
    right: 2%;
    height: 100%;
    padding: 0;
    top: 100%;
}

#height_slider span
{
    display: block;
    margin-left: auto;
    margin-right: auto;
    padding: 0;
}

#height_slider div
{
    position: static;
    height: 90%;
    margin-left: auto;
    margin-right: auto;
}

#height_slider input {
    writing-mode: vertical-lr;
    direction: rtl;
    height: 100%;
    width: 100%;
}
"""
    return "text/css", str(html)

def arrow_svg(state):
    svg = """
 <svg height="512" width="512" xmlns="http://www.w3.org/2000/svg">
  <polygon points="256,8 354,136 288,136 288,504 224,504 224,136 160,136" style="fill:lime;stroke:black;stroke-width:6" />
</svg> 
"""
    return "image/svg+xml", str(svg)

def status_page(state):
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MicroHex: Status Page</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/png" href="/favicon.ico">
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div id="header">
        <h1>MicroHex</h1>
        <div id="NavBar"><span>Status</span><a href="./controller">Controller</a><a href="./calibration">Calibration</a></div>
    </div>
    <div id="main">
        <h2>State Info.</h2>
        <table>
            <tr><td><span>Action: </span></td><td><span id="action">{"Manual" if state["action"] == 0 else "User Controlled" if state["action"] == 1 else "Scripted"}</span></td></tr>
            <tr><td><span>Uptime: </span></td><td><span id="uptime">0:00:00</span></td></tr>
        </table>
    </div>
    <script>
function pad(num, size) {{
    num = num.toString();
    while (num.length < size) num = "0" + num;
    return num;
}}
function GetStatus() {{
    const xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_status");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.onload = function(){{
        state = JSON.parse(xhttp.response);
        uptime = document.querySelector("#uptime");
        seconds = state['uptime'] % 60;
        minutes = Math.floor(state['uptime'] / 60) % 60;
        hours = Math.floor(state['uptime'] / 3600);
        uptime.innerHTML = hours.toString() + ":" + pad(minutes, 2) + ":" + pad(seconds, 2);
        
        setTimeout(GetStatus(), 1000);
    }}
    xhttp.send();
}}

window.onload = function(){{
    GetStatus();
}}
    </script>
</body>
</html>"""
    return "text/html", str(html)

def control_page(state):
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MicroHex: Controller</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/png" href="/favicon.ico">
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div id="header">
        <h1>MicroHex</h1>
        <div id="NavBar"><a href="./">Status</a><span>Controller</span><a href="./calibration">Calibration</a></div>
    </div>
    <div id="main">
        <h2>Actions</h2>
        <div id="action_modes">
            <button {"id='default'" if state["action"] == 2 else ""} type="button" onclick="SetMode(2, this)">Scripted</button>
            <button {"id='default'" if state["action"] == 1 or state["action"] == 0 else ""} type="button" onclick="SetMode(1, this)">User Control</button>
        </div>
        <div id="control_area">
            <div id="user_controls">
                <img id="up_arrow" src="/arrow.svg"/>
                <img id="left_arrow" src="/arrow.svg"/>
                <img id="right_arrow" src="/arrow.svg"/>
                <img id="down_arrow" src="/arrow.svg"/>
                <img id="r_right_arrow" src="/arrow.svg"/>
                <img id="r_left_arrow" src="/arrow.svg"/>
                <div id="speed_slider">
                    <span>Speed</span>
                    <div><input id="speed" class="slider" type="range" min='.1' max='1' step='.1' value='.8' onchange="UpdateSpeed();" oninput="UpdateSpeed();"></div>
                </div>
                <div id="plane_controls">
                    <button id="level_button" type="button" onclick="levelPlane();">Level</button>
                    <div id="plane_range">
                        <div id="plane_center"></div>
                        <div id="plane_point"></div>
                    </div>
                </div>
                <div id="height_slider">
                    <span>Height</span>
                    <div><input id="height" class="slider" type="range" min='-1' max='1' step='.1' value='.5' onchange="UpdatePlane();" oninput="UpdatePlane();"></div>
                </div>
            </div>
        </div>
    </div>
    <script src="/controller.js"></script>
    <script>
let gMode = {state["action"]};
let gFwd = 0;
let gLeft = 0;
let gRotate = 0;
let gDragging = false;
    </script>
</body>
</html>"""
    return "text/html", str(html)

def control_js(state):
    js = f"""
function UpdateSpeed() {{
    speed = document.querySelector("#speed").value
    msg = {{"action": "speed", "speed":speed}}
    
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/rpc");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(msg));
}}

function levelPlane() {{
    plane_range = document.querySelector("#plane_range");
    plane_range.x_angle = 0;
    plane_range.y_angle = 0;
    
    const rect = plane_range.getBoundingClientRect();
    const radius = rect.width/2;
    
    plane_point = document.querySelector("#plane_point");
    plane_point.style.left = "50%";
    plane_point.style.top = "50%";
    
    UpdatePlane();
}}

function dragTo(point_x, point_y) {{
    plane_range = document.querySelector("#plane_range");
    const rect = plane_range.getBoundingClientRect();
    const radius = rect.width/2;
    const center_x = rect.left + radius;
    const center_y = rect.top + radius;

    let dx = point_x - center_x;
    let dy = point_y - center_y;

    const distance = Math.sqrt(dx * dx + dy * dy);
    if (distance > radius) {{
        const angle = Math.atan2(dy, dx);
        dx = Math.cos(angle) * radius;
        dy = Math.sin(angle) * radius;
    }}

    plane_point.style.left = dx+radius + "px";
    plane_point.style.top = dy+radius + "px";

    const last_x = plane_range.x_angle ?? 0;
    const last_y = plane_range.y_angle ?? 0;
    const x = dx/radius;
    const y = dy/radius;

    plane_range.last_x_angle = last_x;
    plane_range.last_y_angle = last_y;
    plane_range.x_angle = x;
    plane_range.y_angle = y;

    diff_x = last_x-x;
    diff_y = last_y-y;
    const d2 = Math.sqrt(diff_x*diff_x + diff_y*diff_y);
    if(d2 > .02){{
        console.log("D2: "+d2);
        plane_range.last_x_angle = x;
        plane_range.last_y_angle = y;

        UpdatePlane();
    }}
}}

function attachButton(button, key) {{
    press = function(button, key) {{
        button.classList.add('pressed');
        
        switch(key) {{
            case 0: gFwd = 1; break;
            case 1: gLeft = 1; break;
            case 2: gLeft = -1; break;
            case 3: gFwd = -1; break;
            case 4: gRotate = -1; break;
            case 5: gRotate = 1; break;
        }}
        
        SendRPC({{"action": "move", "fwd":gFwd, "left":gLeft, "rotate":gRotate}});
    }}
    release = function(button, key) {{
        button.classList.remove('pressed');
        
        switch(key) {{
            case 0: gFwd = 0; break;
            case 1: gLeft = 0; break;
            case 2: gLeft = 0; break;
            case 3: gFwd = 0; break;
            case 4:
            case 5: gRotate = 0; break;
        }}
        
        SendRPC({{"action": "move", "fwd":gFwd, "left":gLeft, "rotate":gRotate}});
    }}

    button.onmousedown = function() {{press(button, key)}};
    button.onmouseup = function() {{release(button, key)}};
    button.ontouchstart = function(e) {{
        press(button, key);
        
        e.preventDefault();
        e.stopPropagation();
        this.style.userSelect = "none";
    }};
    button.ontouchend = function(e) {{
        release(button, key);
        
        e.preventDefault();
        e.stopPropagation();
        this.style.userSelect = "none";
    }};
    
    button.oncontextmenu = function(e) {{
        e.preventDefault();
        e.stopPropagation(); // not necessary in my case, could leave in case stopImmediateProp isn't available? 
        e.stopImmediatePropagation();
        return false;
    }};
}}

window.onload = function(){{
    {"SetMode(1);" if state["action"] == 0 else ""}
    
    document.querySelector("#default").classList.add("active");
    console.log("OnLoad");
    
    attachButton(document.querySelector("#up_arrow"), 0)
    attachButton(document.querySelector("#left_arrow"), 1)
    attachButton(document.querySelector("#right_arrow"), 2)
    attachButton(document.querySelector("#down_arrow"), 3)
    attachButton(document.querySelector("#r_right_arrow"), 4)
    attachButton(document.querySelector("#r_left_arrow"), 5)
    
    if(gMode == 1)
        document.querySelector("#user_controls").style.display='block';
    else
        document.querySelector("#user_controls").style.display='none';
    
    plane_point = document.querySelector("#plane_point");
    plane_point.onmousedown = function () {{ gDragging=true; }};
    document.onmouseup = function () {{ gDragging=false; }};
    document.onmousemove = function(e) {{
        if(!gDragging) return;
        
        dragTo(e.clientX, e.clientY);
    }}
    plane_point.ontouchstart = plane_point.onmousedown;
    document.ontouchend = document.onmouseup;
    
    document.addEventListener('touchmove', (e) => {{
        if (!gDragging || e.touches.length === 0) return;
        const touch = e.touches[0];
        
        dragTo(touch.clientX, touch.clientY);
    }}, {{ passive: false }});
}}

function UpdatePlane() {{
    height = document.querySelector("#height").value
    range = document.querySelector("#plane_range");
    const max_angle = 10.0;
    const max_height = 10.0;
    msg = {{"height":height*max_height, "x_angle":(range.x_angle ?? 0)*max_angle, "y_angle":(range.y_angle ?? 0)*max_angle}}
    
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/update_plane");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(msg));
}}

function SendRPC(msg) {{
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/rpc");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(msg));
}}

function SetMode(mode, element) {{
  if(gMode == mode)
      return;
  
  gMode = mode;
  
  if(gMode == 1)
      document.querySelector("#user_controls").style.display='block';
  else
      document.querySelector("#user_controls").style.display='none';
  
  buttons = document.querySelectorAll("button");
  buttons.forEach((button) => {{
      button.classList.remove("active");
      console.log(button);
  }})
  if(element) element.classList.add("active");
  
  if(gMode == 1)
      msg = {{"action": "user"}};
  else if(gMode == 2)
      msg = {{"action": "script"}};
  
  SendRPC(msg);
}}
"""
    return "text/javascript", str(js)

def calibration_page(state):
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MicroHex: Status Page</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/png" href="/favicon.ico">
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div id="header">
        <h1>MicroHex</h1>
        <div id="NavBar"><a href="./status">Status</a><a href="./controller">Controller</a><span>Calibration</span></div>
    </div>
    <div id="main">
        <h2>Servos</h2>
        <button onclick="SaveServoInfo()">Save</button>
        <div id="servo_list">
        </div>
    </div>
    <script>
function SaveServoInfo() {{
    const xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/save_servo_info");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send();
}}
    
function GetServoInfo(handler) {{
    const xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_servo_info");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.onload = function(){{handler(xhttp)}};
    xhttp.send();
}}

function UpdateServo(msg) {{
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/update_servo");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(msg));
}}

function UpdateInfo(index) {{
    min_val = document.querySelector("#min_"+index).value;
    max_val = document.querySelector("#max_"+index).value;
    cur_val = document.querySelector("#cur_"+index).value;
    off_val = document.querySelector("#off_"+index).value;
    
    msg = {{"index":index, "min":min_val, "max":max_val, "current":cur_val, "offset":off_val}};
    UpdateServo(msg)
}}

window.onload = function(){{
    msg = {{"action": "manual"}};
    const xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/rpc");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(msg));
    
    GetServoInfo(function(req) {{
        console.log(req);
        info = JSON.parse(req.response);
        page = "<table><tr><th>Index</th><th>Min</th><th>Max</th><th>Current</th><th>Offset</th></tr>";
        for(let i=0; i<info.length; i++)
        {{
            line = "<tr>";
            line += "<td>"+i+"</td>";
            line += "<td><input id='min_"+i+"' type='number' min='0' max='180' step='0.1' value='"+info[i]["min"]+"'></td>";
            line += "<td><input id='max_"+i+"' type='number' min='0' max='180' step='0.1' value='"+info[i]["max"]+"'></td>";
            line += "<td><input id='cur_"+i+"' type='number' min='0' max='180' step='0.1' value='"+info[i]["current"]+"'></td>";
            line += "<td><input id='off_"+i+"' type='number' min='0' max='180' step='0.1' value='"+info[i]["offset"]+"'></td>";
            line += "<td><button onclick='UpdateInfo("+i+")'>Update</button></td>";
            line += "</tr>";
            page += line;
        }}
        page += "</table>"
        document.querySelector("#servo_list").innerHTML = page;
    }})
}}
    </script>
</body>
</html>"""
    return "text/html", str(html)
