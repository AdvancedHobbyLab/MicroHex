try:
  import usocket as socket
except:
  import socket

import select
import json

import Pages

class Server():
    def __init__(self, control):
        self.control = control
        
        self.addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(self.addr)
        self.s.listen()
        self.s.setblocking(0)
        
        self.sockets = [self.s]
        self.addrs = {}
        
        print('Listening on', self.addr)
    
    def poll(self):
        readable, _, _ = select.select(self.sockets, [], [], 0)
        
        for sock in readable:
            if sock == self.s:
                conn, addr = sock.accept()
                self.sockets.append(conn)
                self.addrs[conn] = addr
            else:
                try:
                    # Receive and parse the request
                    request = sock.recv(1024)
                    request = str(request)

                    try:
                        request = request.split()
                        method = request[0][2:]
                        if method == "POST":
                            post = request[len(request)-1]
                            post = json.loads(post[post.find("{"):post.rfind("}")+1])
                        else:
                            post = ""
                        request = request[1]
                        
                        #print(f"Recieved {self.addrs[sock]}: {method} {request}")
                    except IndexError:
                        pass
                    
                    state = self.control.get_state()

                    # Generate response
                    if request == '/rpc':
                        content = "application/json"
                        response = "{'status': 'OK'}"
                        if post["action"] == "script":
                            self.control.script()
                        if post["action"] == "user":
                            self.control.auto()
                        if post["action"] == "manual":
                            self.control.manual()
                        if post["action"] == "move":
                            self.control.move(post['fwd'], post['left'], post['rotate'])
                        if post["action"] == "speed":
                            self.control.set_speed(float(post['speed']))
                    elif request == "/get_status":
                        content = "application/json"
                        status = {"state": state["action"], "uptime":self.control.get_uptime()}
                        response = json.dumps(status)
                    elif request == "/get_servo_info":
                        content = "application/json"
                        response = []
                        for i in range(18):
                            servo = self.control.get_servo(i)
                            response.append({"min":servo.get_min_angle(), "max":servo.get_max_angle(), "current":servo.get_angle(), "offset":servo.get_offset()})
                        response = json.dumps(response)
                    elif request == "/save_servo_info":
                        content = "application/json"
                        response = "{'status': 'OK'}"
                        self.control.save_config()
                    elif request == "/update_servo":
                        content = "application/json"
                        response = "{'status': 'OK'}"
                        print(f"Update Servo {post['index']}: Min:{post['min']} Max:{post['max']} Cur:{post['current']} Off:{post['offset']}")
                        servo = self.control.get_servo(int(post['index']))
                        servo.set_angle(float(post['current']))
                        servo.set_min_angle(float(post['min']))
                        servo.set_max_angle(float(post['max']))
                        servo.set_offset(float(post['offset']))
                    elif request == "/update_plane":
                        content = "application/json"
                        response = "{'status': 'OK'}"
                        #print(f"Update Plane: {post['height']}, {post['x_angle']}, {post['y_angle']}")
                        self.control.set_plane(float(post['height']), float(post['x_angle']), float(post['y_angle']))
                    elif request == "/favicon.ico":
                        content = "image/png"
                        with open("favicon.ico", "rb") as f:
                            response = f.read()
                    elif request == '/style.css':
                        content, response = Pages.stylesheet(state)
                    elif request == '/arrow.svg':
                        content, response = Pages.arrow_svg(state)
                    elif request == '/controller':
                        content, response = Pages.control_page(state)
                    elif request == '/controller.js':
                        content, response = Pages.control_js(state)
                    elif request == '/calibration':
                        content, response = Pages.calibration_page(state)
                    else:
                        content, response = Pages.status_page(state)

                    # Send the HTTP response and close the connection
                    sock.send(f'HTTP/1.0 200 OK\r\nContent-type: {content}\r\n\r\n')
                    sock.send(response)
                    sock.close()
                    self.sockets.remove(sock)
                    self.addrs.pop(sock)

                except OSError as e:
                    sock.close()
                    self.sockets.remove(sock)
                    print('Connection closed')
