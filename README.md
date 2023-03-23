This script generates a report based on the StatsD metrics that are fed into InfluxDB.

Sample report:
```
Connections Accepted:  43,354,291 (96.0%) of 45,150,171 attempted
Messages Accepted:     30,089,206 (55.6%) of 54,113,438 attempted

Punishment Detail:
Total                   5,978,401
write before banner:    3,434,647 (57.5%)
three strikes:             91,190 (1.5%)
fake auth:              2,452,564 (41.0%)

Reverse DNS Detail:
error:                  1,792,729 (4.0%)
match:                 37,273,214 (82.6%)
mismatch:               1,533,896 (3.4%)
unknown:                4,548,994 (10.1%)

ACL Accept Detail:
Total:                  5,502,718
mx-accept.dnsal:        5,502,718 (100.0%)

ACL Block Detail:
Total:                    877,624
deny-from.dnsbl:            7,415 (0.8%)
mx-deny.dnsbl:             19,830 (2.3%)
pbl.dnsbl:                 53,346 (6.1%)
sbl.dnsbl:                353,616 (40.3%)
sip.dnsbl:                208,469 (23.8%)
xbl.dnsbl:                234,948 (26.8%)

ACL Trust Detail:
Total:                        718
mx-trust.dnsal:               718 (100.0%)

Filter Accept Detail:
Total                       1,090 (0.0%) of 43,346,872 scanned
recipient                   1,090 (100.0%)

Filter Reject Detail:
Total                     110,746 (0.3%) of 43,346,872 scanned
clamav                        383 (0.3%)
rspamd                    110,363 (99.7%)

Filter Tempfail Detail:
Total                  13,147,450 (30.3%) of 43,346,872 scanned
clamav_error                1,209 (0.0%)
clamav_unknown              5,345 (0.0%)
penaltybox              4,534,229 (34.5%)
rspamd                  8,602,693 (65.4%)
string                      3,974 (0.0%)
```
