#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 

// Socket program configuration
#define TCP_IP "127.0.0.1"
#define TCP_PORT 12222
#define FILE_LEN_BUFFER_SIZE 4 // 32-bit long = 4 bytes

#define MAX_ITERATION 10

// generate a sample xml file
char* gen_xml_file(char* filecontent, const char* ID, int iteration) {
	sprintf(filecontent,
			"<tritoneye>\n"
			"<cameraid>%s</cameraid>\n"
			"<carcnt>%d</carcnt>\n"
			"</tritoneye>",
			ID, iteration);

	return filecontent;
}

void error(const char *msg) {
	perror(msg);
	exit(0);
}

#define FILE_CONTENT_BUFFER_SIZE 4096
int main(int argc, char *argv[]) {
	int sockfd;
	struct sockaddr_in serv_addr;
	struct hostent *server;
	char ID[64];

	int i, file_length;
	char filecontent[FILE_CONTENT_BUFFER_SIZE];

	// Program argument
	// Example: ./client ID_03
	strcpy(ID, "ID_00_FROM_C");
	if (argc == 2)
		strcpy(ID, argv[1]);

	// Create socket
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) error("ERROR opening socket\n");

	server = gethostbyname(TCP_IP);
	if (server == NULL) error("ERROR, no such host\n");

	bzero((char *) &serv_addr, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	bcopy((char *)server->h_addr, 
			(char *)&serv_addr.sin_addr.s_addr,
			server->h_length);
	serv_addr.sin_port = htons(TCP_PORT);
	if (connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) 
		error("ERROR connecting");

	// For each iteration (2 second interval),
	// 1) generate a sample xml file
	// 2) send the file length in 32-bit byte array (so server knows if the file is completely received.)
	// 3) send the file content
	for (i = 0; i < MAX_ITERATION; ++i) {
		gen_xml_file(filecontent, ID, i);
		file_length = strlen(filecontent);

		if (sizeof(file_length) != FILE_LEN_BUFFER_SIZE) {
			error("ASSERTION. The file length is not 32-bit long.");
		}

		write(sockfd, &file_length, FILE_LEN_BUFFER_SIZE);
		write(sockfd, filecontent, file_length);

		sleep(2);
	}

	close(sockfd);

	return 0;
}
