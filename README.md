# MininetPOXSample

controla and topoa:

The network topology depicted in the figure consists of 1 core switch (CS), 4 switches (s1, s2, s3, and s4), 4 hosts (h1, h2, h3, and h4), and one server (Server). All traffic arriving on a switch is forwarded to the controller. It learns the mapping between MAC addresses and ports and installs a flow rule on the switch to handle future packets. So, the only packets that should arrive at the controller are those the switch doesn’t have a flow entry.

controlb and topob:

The topology is modified so that the host h1, h2, h3, and h4 have IP addresses 10.0.1.10/24, 10.0.1.20/24, 10.0.1.30/24, and 10.0.2.10/24 respectively. The SERVER has the IP address 10.0.4.10/24. IP-matching flow rules are installed on switch CS. S1, S2, S3, and S4 stay as a MAC learning switch.

controlc and topob:

A simple firewall has been created at the switch CS. The firewall allows arp and icmp traffic. Any other traffic is dropped except IP traffic from h4. The IP addresses assigned to the hosts and server are same as previous problem (i.e., B).
