#How to build and run

```
docker build -f Dockerfile . -t dns-proxy:test
docker run --rm -it -p 5053:5053/tcp -p 5053:5053/udp dns-proxy:test
```

#Tested record types

- A
- AAAA
- CNAME
- CAA
- DNSKEY
- MX
- TXT

#Sample tests and outputs

```
dig google.com @127.0.0.1 -p 5053 

; <<>> DiG 9.11.2-5-Debian <<>> google.com @127.0.0.1 -p 5053
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 7437
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 6, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		149	IN	A	108.177.119.102
google.com.		149	IN	A	108.177.119.100
google.com.		149	IN	A	108.177.119.101
google.com.		149	IN	A	108.177.119.139
google.com.		149	IN	A	108.177.119.113
google.com.		149	IN	A	108.177.119.138

;; Query time: 125 msec
;; SERVER: 127.0.0.1#5053(127.0.0.1)
;; WHEN: Sun Feb 24 22:10:05 CET 2019
;; MSG SIZE  rcvd: 124
```

```
dig fbi.gov @127.0.0.1 -p 5053 DNSKEY +tcp

; <<>> DiG 9.11.2-5-Debian <<>> fbi.gov @127.0.0.1 -p 5053 DNSKEY +tcp
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 13688
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;fbi.gov.			IN	DNSKEY

;; ANSWER SECTION:
fbi.gov.		8	IN	DNSKEY	256 3 8 QXdFQUFjaHdVRkJkQkRJbGdGV00zQVJKallTcDYwMzRUU2xJMlM0akpF M2tJRThWRjF2cmp5U0VIVFdYQlUyRlpsL01CZi9rVTV3bSt1TlNUYU9t d3E3d3U5MmVLZnJ5Z2psL2UyWXhHdFJvUVpPRUl5OHFXTjJGQmNFRXVF SWMxNDNoTDNLeVNJcGZUU1UrbSt5bEg3bVp5dUloaUI3Y2JUSzdiajRF UTFlRGJISWw=
fbi.gov.		8	IN	DNSKEY	257 3 8 QVFQRnVPaVVsTlVKS0NWVEZaZ1FGcmswc1lKcVBrMXcrTUlsUzI2Uzdt UjhWM0hoWk1TakFzYmRWcUVBd3dpb1dFNzJITVRHSXlFMTA4NG1ia0Z0 SDZBZ1UzM1lJbW5UK0ZkQ3pQcld1RTRFRmxPNnNqaEsveWFJT1hDakpn YzRFZGY0VmQxSm9nbnlDbGREaWtWYVJkQVJ4SG5tU2VCOWV3K3E0WXcy eGlCVXNkeUhxSjJBR0g3WWFZNUlvdk15aGF1YlBqWVdjTEtpbmpzd3E2 OTJFWnZLbnhmZDI2S3NWVm4ydmx4dnFkaVI4cUlNcWI4cmFPUU5tT2po ZkVlcnFqVUFqMkU3K2Mvc001N2R6WkhadXZ3ZWc0Z2pvNkxnaldhbVE2 WHNNMnN2RVNzaXY3OEJEVHh6Z3FZOHNzSXM5Mkx3eUVCUTNPaTZCWHdG WDNvL1VscjE=

;; Query time: 5113 msec
;; SERVER: 127.0.0.1#5053(127.0.0.1)
;; WHEN: Sun Feb 24 22:09:27 CET 2019
;; MSG SIZE  rcvd: 577

```

Note: local modified dnslib exists to address [an issue](https://bitbucket.org/paulc/dnslib/issues/23/dnskey-record-not-properly-encoded) related to string encoding. Also for future testing to add support to allow transparent parsing of different record types like CAA, RRSIG.
