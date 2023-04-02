
import socket
import threading
import sys
import os
import uuid
import json
import tempfile
import time

HOST = ''             
PORT = int(sys.argv[1])        

random = uuid.uuid4()

def process_request(path, socket, type, data):

    print("request type : ", type)
    print("request path : ", path)

    if path.startswith("/api/login"):
        if type == "POST":
            client_response = data.decode('utf-8').split("\r\n\r\n")
            client_respose_cred = client_response[len(client_response) - 1]
            client_respose_cred_json = json.loads(client_respose_cred)

            with open("files/all.txt", "r") as f:
                users = json.loads(f.read())

            # Check if the provided credentials match with any of the usernames and passwords in the file
            for user in users:
                if (user["username"] == client_respose_cred_json["username"] and user["password"] == client_respose_cred_json["password"]):
                    # Extract all tweets made by the user
                    user_tweets = user.get("tweets", [])

                    socket.send('HTTP/1.1 200 OK\r\n'.encode())
                    socket.sendall('Content-Length: {}\r\n\r\n'.format(0).encode())
                    return
                
        elif type == "DELETE": 
            # Delete the cookie to indicate that the user is logged out
            socket.send('Set-Cookie: logged_in=false; Max-Age=0\r\n'.encode())
            socket.send('HTTP/1.1 200 OK\r\n'.encode())
            socket.sendall('Content-Length: {}\r\n\r\n'.format(0).encode())
            return

        else:
            send_404_response(socket)
    
    elif path.startswith("/api/tweet"):
            
        if type == "GET":
            with open("index.html", "r") as rb:
                # reads all the data from the file all.txt
                all_tweets = "[ "
                fileReader2 = open("files/all.txt", "r")
                all_tweets += fileReader2.read()
                fileReader2.close()
                all_tweets += " ]"

            # set the data from the file as response data
            response_data = all_tweets
            print(response_data)
            # check for cookie in client request - if not then set the cookie
            if("Cookie" in data.decode('utf-8')):
                socket.send('HTTP/1.1 200 OK\r\n'.encode())
                socket.send('Content-Length: {}\r\n\r\n'.format(len(all_tweets)).encode())
                socket.send(response_data.encode())
                #print("Response sent data by GET : ", response_data)
            else:
                socket.send('HTTP/1.1 200 OK\r\n'.encode())
                socket.send('Content-Length: {}\r\n'.format(len(all_tweets)).encode())
                cookie = "Set-Cookie: sessionId= {} \r\n\r\n"
                myCookie = cookie.format(random)
                socket.send(myCookie.encode())
                # sends data with response headers
                socket.send(response_data.encode())

        elif type == "POST":
            client_response = data.decode('utf-8').split("\r\n\r\n")
            client_respose_cred = client_response[len(client_response) - 1]
            client_respose_cred_json = json.loads(client_respose_cred)

            print(client_respose_cred_json)

            # Read the existing users from file
            with open("files/all.txt", "r") as file:
                users = json.load(file)
                print(users)

            # Find the user's credentials in the users list
            user_found = False
            for user in users:
                if user["username"] == client_respose_cred_json["username"] and user["password"] == client_respose_cred_json["password"]:
                    user_found = True
                    tweet_id = str(uuid.uuid4())
                    # Add the new tweet to the user's record
                    user["tweets"].append(client_respose_cred_json["tweet"])
                    break

            if user_found:
                # Write the updated users list back to file
                with open("files/all.txt", "w") as file:
                    json.dump(users, file)

                # Send a response back to the client indicating success
                response = "HTTP/1.1 200 OK\r\n\r\n"
                response += "Tweet posted successfully"
                conn.sendall(response.encode())
                conn.close()
            else:
                # Send a response back to the client indicating failure
                response = "HTTP/1.1 401 Unauthorized\r\n\r\n"
                response += "Invalid username or password"
                conn.sendall(response.encode())
                conn.close()


        elif type == "DELETE":
            # Parse the request to get the tweet to be deleted
            print(data)
            path = data.decode('utf-8').split()[1]
            print(path)
            tweet_to_delete = path.split('/')[-1].replace('%20', ' ')

            # Read the existing users from file
            with open("files/all.txt", "r") as file:
                users = json.load(file)

            # Search for the tweet to be deleted
            tweet_deleted = False
            for user in users:
                for i, tweet in enumerate(user["tweets"]):
                    if tweet == tweet_to_delete:
                        del user["tweets"][i]
                        tweet_deleted = True
                        break
                if tweet_deleted:
                    break

            # Write the updated users list back to file
            with open("files/all.txt", "w") as file:
                json.dump(users, file)

            # Send a response back to the client indicating success or failure
            if tweet_deleted:
                response = "HTTP/1.1 200 OK\r\n\r\n"
                response += "Tweet deleted successfully"
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                response += "Tweet not found"
            conn.sendall(response.encode())
            conn.close()

                
        else:   
            send_404_response(socket)
    
    else:
        try:
            # to read files from the file system
            if path.endswith("/"):
                fileReader = open('index.html')
                body = fileReader.read()
                fileReader.close()

                if("Cookies" in data.decode('utf-8')):
                    send_200_response_function(body, True, "text/html", socket)
                else:
                    send_200_response_function(body, False, "text/html", socket)

            elif path.endswith("jpeg"):
                fileReader = open(path[1:], 'rb')
                body = fileReader.read()
                fileReader.close()

                if("Cookies" in data.decode('utf-8')):
                    send_200_response_function(
                        body, True, "images/jpeg", socket)
                else:
                    send_200_response_function(
                        body, False, "images/jpeg", socket)

            elif path.endswith("html"):
                fileReader = open(path[1:])
                body = fileReader.read()
                fileReader.close()

                if("Cookies" in data.decode('utf-8')):
                    send_200_response_function(body, True, "text/html", socket)
                else:
                    send_200_response_function(
                        body, False, "text/html", socket)
            else:
                send_404_response(socket)
                print(path)

        except FileNotFoundError as e:
            send_404_response(socket)
            print(path)
        except Exception as e:
            print(path)
            print(e)

def send_404_response(socket):
    print("Inapproriate file type !")
    socket.send('HTTP/1.1 404 NOT FOUND\r\n\r\n'.encode())
    socket.send(
        b'<html><head></head></body><h1>ERROR 404 PATH NOT FOUND</h1></body></html>')


def send_200_response_function(data_from_File, Cookies, content_type, socket):

    daLength = len(data_from_File)

    socket.send('HTTP/1.1 200 OK\r\n'.encode())
    socket.send('Content-Length: {}\r\n'.format(daLength).encode())

    if Cookies == False:
        cookie = "Set-Cookie: sessionId= {} \r\n\r\n"
        myCookie = cookie.format(random)
        socket.send("Content-Type: {}\r\n".format(content_type).encode())
        socket.send(myCookie.encode())

    else:
        socket.send("Content-Type: {}\r\n\r\n".format(content_type).encode())

    if(content_type != "images/jpeg"):
        socket.sendall(data_from_File.encode())
    else:
        socket.sendall(data_from_File)

# threads to simulate cocurrency
def threading_function(socket):
    try:
        data = socket.recv(1024)
        str_data = data.decode('utf-8')
        parts = str_data.split(" ")
        process_request(parts[1], socket, parts[0], data)
    
    except KeyboardInterrupt as ke:
        print(ke)
        socket.close()

    except Exception as e:
        print("Something happened in threads!")
        socket.close()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        try:
            conn, addr = s.accept()
            threadObj = threading.Thread(target=threading_function, args=(conn, ))
            threadObj.start()
        except Exception as e:
            print(e)
            s.close()
