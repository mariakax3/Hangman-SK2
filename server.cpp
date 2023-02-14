#include <iostream>
#include <fstream>
#include <string>
#include <cstring>
#include <vector>
#include <time.h>
#include <algorithm>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <threads.h>
#include <signal.h>

#define MAX_CLIENTS 64
#define min(a,b)            (((a) < (b)) ? (a) : (b))
#define max(a,b)            (((a) > (b)) ? (a) : (b))
// using namespace std;

struct Player{
    std::string username;
    std::string lives;
    int socket;
};
std::vector<Player> players;

int category = -1;
char clue = '0';
std::string tosend;
char* char_array;
int server_fd;
bool in_game = true;

std::string receive(int client) {
    char data[64]={0};
    recv(client, data , sizeof(data) , 0);
    return std::string(data);
}

int check_username(std::string name) {
    for(Player player : players) {
        if (player.username == name) {
            return -1;
        }
    }
    return 0;
}

Player create_player(std::string name, int sockfd) {
    Player p;
    p.username = name;
    p.lives = "9";
    p.socket = sockfd;
    return p;
}

void get_clue() {
    srand(time(NULL));

    std::string file_name;
    category = rand()%4;
    clue = 'a' + rand()%26;
}

void send_top(int sockfd) {
    std::string top = "";
    for(int i = 0; i < min(8, static_cast<int>(players.size())); i++) {
        top.append(players[i].username).append(":").append(players[i].lives);
        if (i < min(8, static_cast<int>(players.size())) - 1) {
            top.append(";");
        }
    }
    top.append("\r\n");
    std::cout << top;
    write(sockfd, top.c_str(), top.length());
}

bool compare_by_lives(const Player &p1, const Player &p2) {
    return p1.lives > p2.lives;
}

void* handle_client(void* socket) {
    int client_socket = *((int*) socket);

    if (players.size() < 2) {

        while (players.size() < 2);

        write(client_socket, char_array, 2);
        send_top(client_socket);
        std::cout << char_array << std::endl;
    } else {
        write(client_socket, char_array, 2);
        send_top(client_socket);
        std::cout << char_array << std::endl;
    }

    while (in_game) {
        char l[1];
        // std::string l = receive(client_socket);
        int ret = recv(client_socket, l, 1, MSG_DONTWAIT);
        if (ret > 0) { 
            if (std::to_string(l[0]) == "w") {
                in_game = false;
            }
            for(auto & player : players) {
                if (player.socket == client_socket) {
                    player.lives = std::to_string(l[0]);
                    break;
                }
            }
        }
        sort(players.begin(), players.end(), compare_by_lives);
        send_top(client_socket);
        sleep(1);
    }

    std::cout << "end of the game" << std::endl;

    close(client_socket);

    return nullptr;
}

void ctrl_c(int){
    for(auto & player : players){
        shutdown(player.socket, SHUT_RDWR);
        close(player.socket);
    }
    close(server_fd);
    printf("Closing server\n");
    exit(0);
}

int main() {
    int server_socket, client_socket;
    struct sockaddr_in server_address, client_address;
    socklen_t client_len;
    signal(SIGINT, ctrl_c);

    get_clue();
    tosend = std::to_string(category) + clue;

    const int length = tosend.length();
    char_array = new char[length + 1];
    strcpy(char_array, tosend.c_str());

    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    server_fd = server_socket;

    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(8000);
    // server_address.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_address.sin_addr.s_addr = htonl(INADDR_ANY);

    const int enable = 1;
    if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0) {
        perror("Error: Failed to setsockopt(SO_REUSEADDR)");
    }

    if(bind(server_socket, (struct sockaddr *) &server_address, sizeof(server_address)) < 0) {
        perror("Error: Failed to bind server socket");
        return 1;
    }

    listen(server_socket, MAX_CLIENTS);
    std::cout << "Server Listening...\n";

    pthread_t thread;
    int status;

    while (true) {
        printf("Waiting for connections...\n");
        client_len = sizeof(client_address);
        if((client_socket = accept(server_socket, (struct sockaddr *) &client_address, &client_len)) < 0){
            perror("Error: Client failed to connect");
            return 1;
        }
        std::cout << "Connection accepted\n";

        std::string newName = receive(client_socket);
        if (check_username(newName) == -1) {
            std::string message = "taken";
            write(client_socket, message.c_str(), message.length());
        } else {
            std::string message = "available";
            write(client_socket, message.c_str(), message.length());
        }

        players.push_back(create_player(newName, client_socket));

        int* client_ptr = new int(client_socket);
        status = pthread_create(&thread, nullptr, handle_client, (void*)client_ptr);
        if (status != 0) {
            perror("Error: Failed to create thread");
            return 1;
        }
    }

    close(server_socket);

    return 0;
}