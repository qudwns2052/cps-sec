#ifndef ARP_H
#define ARP_H

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
#include <sys/sysctl.h>
#include <netinet/in.h>
#include <unistd.h>
#include <net/if_dl.h>
#include <netinet/in.h>


#define ETH_HEADER_SIZE 14
#define ARP_HEADER_SIZE 28
#define BUF_SIZE 1024


/* ARP header */
struct arp_header
{
    uint16_t hw_type;    /* Hardware Type           */
    uint16_t proto_type; /* Protocol Type           */
    uint8_t hlen;        /* Hardware Address Length */
    uint8_t plen;        /* Protocol Address Length */
    uint16_t oper;       /* Operation Code          */
    uint8_t smac[6];     /* Sender hardware address */
    uint8_t sip[4];      /* Sender IP address       */
    uint8_t dmac[6];     /* Target hardware address */
    uint8_t dip[4];      /* Target IP address       */
};

class Arp
{
public:
    uint8_t packet[50];
    uint8_t request_packet[50];
    uint8_t attack_packet[50];
    uint8_t victim_ip[4];
    char dev[20];

    Arp(char * dev, uint8_t * ip)
    {
        memset(packet, 0x00, 50);
        memcpy(this->dev, dev, strlen(dev));
        memcpy(victim_ip, ip, 4);
    }
    ~Arp()
    {
    }

    void setArp();
    void getMyInfo(uint8_t *subnet, uint8_t *ip, uint8_t *mac);
    void getTargetInfo(uint8_t * my_mac, uint8_t * target_ip, uint8_t *target_mac);
    void sendArp();
};
#endif // ARP_H

