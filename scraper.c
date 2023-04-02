// started with https://www.educative.io/edpresso/how-to-implement-tcp-sockets-in-c
// and the example in https://www.man7.org/linux/man-pages/man3/getaddrinfo.3.html

#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <netdb.h> // For getaddrinfo
#include <unistd.h> // for close
#include <stdlib.h> // for exit
#include <assert.h>

int socket_desc;
struct sockaddr_in server_addr;
char server_message[2000], client_message[2000];
char address[100];
struct addrinfo *result;

int socket_setup(){
    // Clean buffers:
    memset(server_message,'\0',sizeof(server_message));
    memset(client_message,'\0',sizeof(client_message));
    
    // Create socket:
    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    
    if(socket_desc < 0){
        printf("Unable to create socket\n");
        return -1;
    }
    
    printf("Socket created successfully\n");

    struct addrinfo hints;
    memset (&hints, 0, sizeof (hints));
    hints.ai_family = PF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags |= AI_CANONNAME;
    
    // get the ip of the page we want to scrape
    int out = getaddrinfo ("www.cs.umanitoba.ca", NULL, &hints, &result);
    // fail gracefully
    if (out != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(out));
        exit(EXIT_FAILURE);
    }
    
    // ai_addr is a struct sockaddr
    // so, we can just use that sin_addr
    struct sockaddr_in *serverDetails =  (struct sockaddr_in *)result->ai_addr;
    
    // Set port and IP the same as server-side:
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(80);
    //server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_addr = serverDetails->sin_addr;
    
     // converts to octets
    printf("Convert...\n");
    inet_ntop (server_addr.sin_family, &server_addr.sin_addr, address, 100);
    printf("Connecting to %s\n", address);
    // Send connection request to server:
    if(connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0){
        printf("Unable to connect\n");
        exit(EXIT_FAILURE);
    }
    printf("Connected with server successfully\n");
    
    // Get input from the user:
    /* header is:
    GET /~robg/3010/index.html HTTP/1.1
    Host: www.cs.umanitoba.ca
    
    */
    char request[] = "GET /~robg/3010/index.html HTTP/1.1\r\nHost: www.cs.umanitoba.ca\r\n\r\n";
    printf("Sending:\n%s\n", request);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));
    if(send(socket_desc, request, strlen(request), 0) < 0){
        printf("Unable to send message\n");
        return -1;
    }
    // Receive the server's response:
    if(recv(socket_desc, server_message, sizeof(server_message), 0) < 0){
        printf("Error while receiving server's msg\n");
        return -1;
    }
    printf("Server's response: %s\n",server_message);
    // Close the socket:
    close(socket_desc);
    return 1;
}

void socket_close(){
    close(socket_desc);
} 

int post_request(int argc, char *argv[]){
    char *memo = malloc(256);
    fflush(stdout);
    for (int i = 2; i < argc; i++){
        strcat(memo, argv[i]);
        strcat(memo, " ");
    }
    char *request = malloc(1024);
    strcpy(request, "POST /api/tweet HTTP/1.1\r\nHost: localhost\r\nContent-Length: ");
    char result1[strlen(memo)];
    sprintf(result1, "%lu", strlen(memo));
    strcat(request, result1);
    strcat(request, "\r\nCookie: ");
    strcat(request, argv[1]);
    strcat(request, "\r\n\r\n{\"id\" : ");
    strcat(request, "\"");
    for (int i = 2; i < argc; i++){
        strcat(request, argv[i]);if (i != argc - 1){
            strcat(request, " ");
        }
    }
    strcat(request, "\"");
    strcat(request, "}");
    printf("Sending:\n%s\n", request);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));
    if (send(socket_desc, request, strlen(request), 0) < 0){
        printf("Unable to send message\n");
        return -1;
    }
    // Receive the server's response:
    if (recv(socket_desc, server_message, sizeof(server_message), 0) < 0){
        printf("Error while receiving server's msg\n");
        return -1;
    }
    printf("Server's response: %s\n", server_message);
    free(request);
    if (strncmp(server_message, "HTTP/1.1 200 OK", strlen("HTTP/1.1 200 OK")) == 0){
        return 0;
    }
    else{
        return 1;
    }
}
char *get_request(int argc, char *argv[]){
    char *memo = malloc(256);
    fflush(stdout);
    for (int i = 2; i < argc; i++){
        strcat(memo, argv[i]);
        strcat(memo, " ");
    }
    char *request = malloc(1024);
    strcpy(request, "GET /api/tweet HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0");
    strcat(request, "\r\nCookie: ");
    strcat(request, argv[1]);
    strcat(request, "\r\n\r\n");
    printf("Sending:\n%s\n", request);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));
    if (send(socket_desc, request, strlen(request), 0) < 0){
        printf("Unable to send message\n");
        return NULL;
    }
    // Receive the server's response:
    if (recv(socket_desc, server_message, sizeof(server_message), 0) < 0){
        printf("Error while receiving server's msg\n");
        return NULL;
    }
    printf("Server's response: %s\n", server_message);
    free(request);
    return server_message;
}

int delete_request(int argc, char *argv[]){
    char *request = malloc(1024);
    strcpy(request, "DELETE /api/tweet/");
    for (int i = 2; i < argc; i++){
        strcat(request, argv[i]);
        if (i != argc - 1){
            strcat(request, "_");
        }
    }
    strcat(request, " HTTP/1.1\r\nHost: localhost");
    strcat(request, "\r\nCookie: ");
    strcat(request, argv[1]);
    strcat(request, "\r\n\r\n");
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));
    if (send(socket_desc, request, strlen(request), 0) < 0)
    {
        printf("Unable to send message\n");
        return -1;
    }
    // Receive the server's response:
    if (recv(socket_desc, server_message, sizeof(server_message), 0) < 0){
        printf("Error while receiving server's msg\n");
        return -1;
    }
    printf("Server's response: %s\n", server_message);
    free(request);
    if (strncmp(server_message, "HTTP/1.1 200 OK", strlen("HTTP/1.1 200 OK")) == 0){
        return 0;
    }
    else{
        return 1;
    }
}

int main(int argc, char *argv[]){
    assert(socket_setup() == 1);
    char *get_1 = malloc(1024);
    strcpy(get_1, get_request(argc, argv));
    socket_close();

    assert(socket_setup() == 1);
    int ret = post_request(argc, argv);
    if (ret < 0){
        printf("error in post request\n");
        exit(0);
    }
    socket_close();
    assert(socket_setup() == 1);
    char *get_2 = malloc(1024);
    strcpy(get_2, get_request(argc, argv));
    socket_close();
    assert(socket_setup() == 1);

    assert(strcmp(get_2, get_1) != 0);
    if (delete_request(argc, argv) < 0){
        printf("error in delete request\n");
        exit(0);
    }
    socket_close();
    assert(socket_setup() == 1);
    return 0;
}