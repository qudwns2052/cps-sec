#include <algorithm>
#include <arpa/inet.h>
#include <ctype.h>
#include <errno.h>
#include <netinet/ip.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <iostream>
#include <list>
#include <pcap.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <unistd.h>
#include "arp.h"

void signal_handler(int signo) // signal handler
{
    exit(0);
}

int main(int argc, char *argv[])
{
    signal(SIGINT, signal_handler);

    if (argc != 3)
    {
        printf("syntax : <dev> <victim ip>\n");
        return -1;
    }

    char *dev = argv[1];
    
    uint8_t ip[4];
    inet_pton(AF_INET, argv[2], ip);

    Arp *arp = new Arp(dev, ip);
    arp->setArp();
    arp->sendArp();


    delete arp;

    
    return 0;
}
