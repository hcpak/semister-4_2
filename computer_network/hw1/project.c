#include <pcap.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

/* default snap length (maximum bytes per packet to capture) */
#define SNAP_LEN 1518

/* ethernet headers are always exactly 14 bytes [1] */
#define SIZE_ETHERNET 14
//udp headers are always exactly 8 bytes
#define SIZE_UDP 8
/* Ethernet addresses are 6 bytes */
#define ETHER_ADDR_LEN	6


/* IP header */
struct sniff_ip {
        u_char  ip_vhl;                 /* version << 4 | header length >> 2 */
        u_char  ip_tos;                 /* type of service */
        u_short ip_len;                 /* total length */
        u_short ip_id;                  /* identification */
        u_short ip_off;                 /* fragment offset field */
        #define IP_RF 0x8000            /* reserved fragment flag */
        #define IP_DF 0x4000            /* dont fragment flag */
        #define IP_MF 0x2000            /* more fragments flag */
        #define IP_OFFMASK 0x1fff       /* mask for fragmenting bits */
        u_char  ip_ttl;                 /* time to live */
        u_char  ip_p;                   /* protocol */
        u_short ip_sum;                 /* checksum */
        struct  in_addr ip_src,ip_dst;  /* source and dest address */
};
#define IP_HL(ip)               (((ip)->ip_vhl) & 0x0f)
#define IP_V(ip)                (((ip)->ip_vhl) >> 4)

/* TCP header */
typedef u_int tcp_seq;

struct sniff_tcp {
        u_short th_sport;               /* source port */
        u_short th_dport;               /* destination port */
        tcp_seq th_seq;                 /* sequence number */
        tcp_seq th_ack;                 /* acknowledgement number */
        u_char  th_offx2;               /* data offset, rsvd */
#define TH_OFF(th)      (((th)->th_offx2 & 0xf0) >> 4)
        u_char  th_flags;
        #define TH_FIN  0x01
        #define TH_SYN  0x02
        #define TH_RST  0x04
        #define TH_PUSH 0x08
        #define TH_ACK  0x10
        #define TH_URG  0x20
        #define TH_ECE  0x40
        #define TH_CWR  0x80
        #define TH_FLAGS        (TH_FIN|TH_SYN|TH_RST|TH_ACK|TH_URG|TH_ECE|TH_CWR)
        u_short th_win;                 /* window */
        u_short th_sum;                 /* checksum */
        u_short th_urp;                 /* urgent pointer */
};
//udp header
struct	sniff_udp{
	u_short th_sport;
	u_short th_dport;
	u_short udp_len;
	u_short udp_chksum;
};// total udp header length: 8 bytes


void
got_dns_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet);

void
got_http_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet);

void // To show dns_header
got_dns_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet){
	static int count = 1;                   /* packet counter */
	
	/* declare pointers to packet headers */
	//const struct sniff_ethernet *ethernet;  /* The ethernet header [1] */
	const struct sniff_ip *ip;              /* The IP header */
	const struct sniff_udp *udp;            /* The udP header */
	const char *payload;                    /* Packet payload */

	int size_ip;
	
	/* define/compute ip header offset */
	ip = (struct sniff_ip*)(packet + SIZE_ETHERNET);
	size_ip = IP_HL(ip)*4;
	if (size_ip < 20) {
		printf("   * Invalid IP header length: %u bytes\n", size_ip);
		return;
	}

	/* define/compute udp header offset */
	udp = (struct sniff_udp*)(packet + SIZE_ETHERNET + size_ip);
	
	
	/* define/compute udp payload (segment) offset */
	payload = (u_char *)(packet + SIZE_ETHERNET + size_ip + SIZE_UDP);
	// If the udp header exists on port 53, so does the dns header.
    //show #No S_IP:S_Port D_IP:D_Port
    printf("%d %s:%d",count++, inet_ntoa(ip->ip_src),ntohs(udp->th_sport));
	printf(" %s:%d DNS ID : ",inet_ntoa(ip->ip_dst), ntohs(udp->th_dport));	
	u_char * ch= payload;
    // show DNS_ID [0x format]
	for(int i = 0; i<2;i++){
		printf("%02x",*ch);
		ch++;
	}
	printf("\n");
    //show [QR|Opcode|AA|TC|RD|RA|Z|RCODE]
	printf("%c | %c%c%c%c | %c | %c | %c",(*ch)&(0x80)?'1':'0',(*ch)&(0x40)?'1':'0',(*ch)&0x20?'1':'0',(*ch)&0x10?'1':'0',
		((*ch)&0x08)?'1':'0',(*ch)&0x04?'1':'0',(*ch)&0x02?'1':'0', (*ch)&0x01?'1':'0');
	ch++;
	printf(" | %c | %c%c%c | %c%c%c%c\n",(*ch)&0x80?'1':'0',(*ch)&0x40?'1':'0',(*ch)&0x20?'1':'0',(*ch)&0x10?'1':'0',
		(*ch)&0x08?'1':'0',(*ch)&0x04?'1':'0',(*ch)&0x02?'1':'0', (*ch)&0x01?'1':'0');
	ch++;
    //show QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT [decimal format]
	printf("QDCOUNT: %d\n",(*ch)*256+(*(ch+1)));
	ch = ch+2;
	printf("ANCOUNT: %d\n",(*ch)*256+(*(ch+1)));
	ch = ch+2;
	printf("NSCOUNT: %d\n",(*ch)*256+(*(ch+1)));
	ch = ch+2;
	printf("ARCOUNT: %d\n\n",(*ch)*256+(*(ch+1)));
	
}

//To show HTTP_Header
void
got_http_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet)
{

	static int count = 1;                   /* packet counter */
	
	/* declare pointers to packet headers */
	//const struct sniff_ethernet *ethernet;  /* The ethernet header [1] */
	const struct sniff_ip *ip;              /* The IP header */
	const struct sniff_tcp *tcp;            /* The TCP header */
	const char *payload;                    /* Packet payload */

	int size_ip;
	int size_tcp;
	int size_payload;
    
	/* define/compute ip header offset */
	ip = (struct sniff_ip*)(packet + SIZE_ETHERNET);
	size_ip = IP_HL(ip)*4;
	if (size_ip < 20) {
		printf("   * Invalid IP header length: %u bytes\n", size_ip);
		return;
	}
	
	// This packet is TCP.

	/* define/compute tcp header offset */
	tcp = (struct sniff_tcp*)(packet + SIZE_ETHERNET + size_ip);
	size_tcp = TH_OFF(tcp)*4;
	if (size_tcp < 20) {
		printf("   * Invalid TCP header length: %u bytes\n", size_tcp);
		return;
	}
    
	/* define/compute tcp payload (segment) offset */
	payload = (u_char *)(packet + SIZE_ETHERNET + size_ip + size_tcp);
	
	/* compute tcp payload (segment) size */
	size_payload = ntohs(ip->ip_len) - (size_ip + size_tcp);
    if (size_payload > 0) {
		//show #No S_IP:S_Port D_IP:D_Port
		printf("%d %s:%d",count++, inet_ntoa(ip->ip_src),ntohs(tcp->th_sport));
		printf(" %s:%d ",inet_ntoa(ip->ip_dst), ntohs(tcp->th_dport));
        //show HTTP [Request|Response] : Depending on whether port 80 is in the source or destination, it is "Response" and "Request" respectively.
		if(ntohs(tcp->th_sport) == 80){
			printf("HTTP Response\n");
		}else{
			printf("HTTP Request\n");
		}
		u_char * ch= payload;
        //parsing until meet \r\n\r\n
		u_char *pt = strstr(payload, "\r\n\r\n");
        for(int i = 0; i<size_payload; i++){
            if(pt == ch)
                break;
            if(isprint(*ch))
                printf("%c",*ch);
            else
                printf(".");
			ch++;
		}
		printf("\n\n");
	}

return;
}

int main(int argc, char **argv)
{
    pcap_if_t *alldevs;         //capture device name
	char errbuf[PCAP_ERRBUF_SIZE];		/* error buffer */
	pcap_t *handle;				/* packet capture handle */

    char filter_exp[] = "port 53";		/* filter expression [3] */
	struct bpf_program fp;			/* compiled filter program (expression) */
	bpf_u_int32 mask;			/* subnet mask */
	bpf_u_int32 net;			/* ip */
	int num_packets = 100;			/* number of packets to capture */
	int filter_num=1;			// meaning of 1 is HTTP HEADER and meaning of 2 is DNS HEADER
    
    // find all device which is connected network
    if(pcap_findalldevs(&alldevs, errbuf) ==-1){
        fprintf(stderr, "Error in pcap_findalldevs: %s\n",errbuf);
    }
    /* get network number and mask associated with capture device */
    if (pcap_lookupnet(alldevs->name, &net, &mask, errbuf) == -1) {
        fprintf(stderr, "Couldn't get netmask for device %s: %s\n",
            alldevs->name, errbuf);
        net = 0;
        mask = 0;
    }
    
    int i=0; // count device num
    for(pcap_if_t *d=alldevs; d; d=d->next){
        printf("%d. %s", ++i, d->name);
        if(d->description)
            printf(" ( %s )\n", d->description);
        else
            printf(" (No description available)\n");
    }
    if(i==0){
        printf("\nNo interfaces found! Make sure libpcap is install.\n");
        return -1;
    }
    
    //interface
	printf("whcih header do you want to sniff? Enter the number (HTTP=1, DNS =2):");
	scanf("%d",&filter_num);
	if(filter_num ==1){ // If you choose 1, Then change filter port 80
		filter_exp[5]='8';
		filter_exp[6]='0';
	}
	
    
    handle = pcap_open_live(alldevs->name, SNAP_LEN, 1, 1000, errbuf);
    if (handle == NULL) {
        fprintf(stderr, "Couldn't open device %s: %s\n", alldevs->name, errbuf);
        pcap_freealldevs(alldevs);
        exit(EXIT_FAILURE);
    }
    
	/* make sure we're capturing on an Ethernet device [2] */
	if (pcap_datalink(handle) != DLT_EN10MB) {
		fprintf(stderr, "%s is not an Ethernet\n", alldevs->name);
		exit(EXIT_FAILURE);
	}

	/* compile the filter expression */
	if (pcap_compile(handle, &fp, filter_exp, 0, net) == -1) {
		fprintf(stderr, "Couldn't parse filter %s: %s\n",
		    filter_exp, pcap_geterr(handle));
		exit(EXIT_FAILURE);
	}

	/* apply the compiled filter */
	if (pcap_setfilter(handle, &fp) == -1) {
		fprintf(stderr, "Couldn't install filter %s: %s\n",
		    filter_exp, pcap_geterr(handle));
		exit(EXIT_FAILURE);
	}
    
    //Delete the Linked List that was created through pcap_findalldevs
    pcap_freealldevs(alldevs);

	/* now we can set our callback function */
    //And
	if(filter_num ==2){// if choose DNS Header, then callback function is got_dns_packet
		while(1)
            pcap_loop(handle, num_packets, got_dns_packet, NULL);
	}else{// if choose HTTP Header, then callback function is got_http_packet
		while(1)
			pcap_loop(handle, num_packets, got_http_packet, NULL);
	}

	/* cleanup */
	pcap_freecode(&fp);
	pcap_close(handle);

return 0;
}

