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

#define MAX_CLIENTS 64
using namespace std;

struct Player{
    string username;
    string lives;
    int socket;
};
vector<Player> players;

int category = -1;
char clue = '0';
string tosend;
char* char_array;

string receive(int client) {
    char data[64]={0};
    recv(client, data , sizeof(data) , 0);
    return string(data);
}

int check_username(string name) {
    for(Player player : players) {
        if (player.username == name) {
            return -1;
        }
    }
    return 0;
}

Player create_player(string name, int sockfd) {
    Player p;
    p.username = name;
    p.lives = '9';
    p.socket = sockfd;
    return p;
}

void get_clue() {
    srand(time(NULL));

    string file_name;
    category = rand()%4;
    clue = 'a' + rand()%26;
}

void send_top(int sockfd) {
    string top = "";
    for(int i = 0; i < min(8, static_cast<int>(players.size())); i++) {
        top.append(players[i].username).append(":").append(players[i].lives).append(";");
    }
    cout << top << endl;
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
        cout << char_array << endl;
    } else {
        write(client_socket, char_array, 2);
        send_top(client_socket);
        cout << char_array << endl;
    }

    for(int i = 0; i < 10; i++) {
        string l = receive(client_socket);
        if (l == "w") { //win
            string winner;
            for(auto & player : players) {
                if (player.socket == client_socket) {
                    winner = player.username;
                    winner = winner.append(";");
                    break;
                }
            }
            for(auto & player : players) { //send winner username to other players
                if (player.socket != client_socket) {
                    write(player.socket, winner.c_str(), winner.length());
                }
            }
            cout << "player " << client_socket << " won" << endl;
        }
        for(auto & player : players) {
            if (player.socket == client_socket) {
                player.lives = l;
                break;
            }
        }
        sort(players.begin(), players.end(), compare_by_lives);
        send_top(client_socket);
    }

    cout << "end of the game" << endl;

    close(client_socket);

    return nullptr;
}

int main() {
    int server_socket, client_socket;
    struct sockaddr_in server_address, client_address;
    socklen_t client_len;

    get_clue();
    tosend = to_string(category) + clue;

    const int length = tosend.length();
    char_array = new char[length + 1];
    strcpy(char_array, tosend.c_str());

    server_socket = socket(AF_INET, SOCK_STREAM, 0);

    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(8000);
    server_address.sin_addr.s_addr = inet_addr("127.0.0.1");
    // server_address.sin_addr.s_addr = htonl(INADDR_ANY);

    if(bind(server_socket, (struct sockaddr *) &server_address, sizeof(server_address)) < 0) {
        perror("Error: Failed to bind server socket");
        return 1;
    }

    listen(server_socket, MAX_CLIENTS);
    cout << "Server Listening...\n";

    pthread_t thread;
    int status;

    while (true) {
        printf("Waiting for connections...\n");
        client_len = sizeof(client_address);
        if((client_socket = accept(server_socket, (struct sockaddr *) &client_address, &client_len)) < 0){
            perror("Error: Client failed to connect");
            return 1;
        }
        cout << "Connection accepted\n";

        string newName = receive(client_socket);
        if (check_username(newName) == -1) {
            string message = "taken";
            write(client_socket, message.c_str(), message.length());
        } else {
            string message = "available";
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