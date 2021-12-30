'''
Roll no : 2021H1030103P
Conroller for question C
'''

from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

log = core.getLogger()

'''
The mac_to_port data structure at the controller stores the mapping between mac address and port for every switch. It is actually a dictionary of dictionaries.
The key for the outer dictionary is the switch dpid. The value for the outer dictionary is another dictionary whose keys are mac addresses of hosts in the network.
The value for the inner dictionary is port through which we can reach the host having the mac address specified in the key from the switch mentioned in the key of outer dictionary.
eg: mac_to_port={5:{{40:10:40:10:40:10,2},{40:10:40:10:40:20,1}},4:{{40:10:40:10:40:10,6},{40:10:40:10:40:20,3}}}
In this example, first key of outer dictionary is 5. This is dpid of a switch. So, this means that to reach host with mac address 40:10:40:10:40:10 from switch 5, you have to forward to port 2.
To reach host with mac address 40:10:40:10:40:20 from switch 5, you have to forward to port 1.
To reach host with mac address 40:10:40:10:40:10 from switch 4, you have to forward to port 6
To reach host with mac address 40:10:40:10:40:20 from switch 4, you have to forward to port 3
'''
mac_to_port = {}

'''
The ip_to_mac data structure at the controller stores the mapping between ip addresses and the mac address of hosts
'''
ip_to_mac = {'10.0.1.10':'00:00:00:00:00:0A','10.0.1.20':'00:00:00:00:00:0B','10.0.1.30':'00:00:00:00:00:0C','10.0.2.10':'00:00:00:00:00:0D','10.0.4.10':'00:00:00:00:00:0E'}

'''
The ip_to_cs_port data structure at the controller stores the port through with the host with the ip address can be reached from the central switch s5
eg: Host with IP address 10.0.1.10 can be reached from s5 through port 1
'''
ip_to_cs_port = {'10.0.1.10':1, '10.0.1.20':5,'10.0.1.30':4,'10.0.2.10':3,'10.0.4.10':2}

'''
handle ConnectionUp :
fired in response to the establishment of a new control channel with a switch.
'''
def _handle_ConnectionUp(event):
	global ip_to_mac,ip_to_cs_port,mac_to_port
	print("Switch ",event.connection.dpid)
	print(dpid_to_str(event.connection.dpid))
	for swprt in event.connection.features.ports:
		print(swprt.name)
	#Initialise the outer dictionary with key values as switch dpids as the connection with switch gets established and with empty values for every switch except cs(s5) since it is not a learning switch
	if(event.connection.dpid!=5):
		mac_to_port[event.connection.dpid]={}
	#Adding the IP matching rules in cs(s5)
	#Based on the ip_to_mac and ip_to_cs_port data structure values, the rules are added
	#Since the various hosts are in various subnets, the switch CS acts as a router and modifies the packet header fields as part of the rule actions, so that the packet gets forwarded properly from cs
	#Among IP, The firewall allows only ICMP packets and IP traffic from h4
	else:
		#The first 5 rules are for allowing ICMP traffic through cs (s5)
		#flow_mod is for adding the flow rule
		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.match.nw_proto = 1 #nw_proto for ICMP packets
		msg.match.dl_type = 0x0800 #dl_type for IP packets
		msg.match.nw_dst = '10.0.1.10'
		msg.actions.append(of.ofp_action_dl_addr.set_src("00:00:00:00:00:05"))
		#Since various subnets are there, as part of the action in flow rules the source MAC address in the packet header field is changed to the MAC address of the switch cs ie, 00:00:00:00:00:05
		msg.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac['10.0.1.10']))
		#Since there are various subnets, the the destiantion MAC address in the packet header field needs to be changed, which can be obtained from the ip_to_mac data structure
		msg.actions.append(of.ofp_action_output(port = ip_to_cs_port['10.0.1.10']))
		event.connection.send(msg)
		log.debug("Flow rule for ICMP traffic for destination 10.0.1.10 added at cs (s5)")

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.match.nw_proto = 1
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = '10.0.1.20'
		msg.actions.append(of.ofp_action_dl_addr.set_src("00:00:00:00:00:05"))
		msg.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac['10.0.1.20']))
		msg.actions.append(of.ofp_action_output(port = ip_to_cs_port['10.0.1.20']))
		event.connection.send(msg)
		log.debug("Flow rule for ICMP traffic for destination 10.0.1.20 added at cs (s5)")

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.match.nw_proto = 1
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = '10.0.1.30'
		msg.actions.append(of.ofp_action_dl_addr.set_src("00:00:00:00:00:05"))
		msg.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac['10.0.1.30']))
		msg.actions.append(of.ofp_action_output(port = ip_to_cs_port['10.0.1.30']))
		event.connection.send(msg)
		log.debug("Flow rule for ICMP traffic for destination 10.0.1.30 added at cs (s5)")

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.match.nw_proto = 1
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = '10.0.2.10'
		msg.actions.append(of.ofp_action_dl_addr.set_src("00:00:00:00:00:05"))
		msg.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac['10.0.2.10']))
		msg.actions.append(of.ofp_action_output(port = ip_to_cs_port['10.0.2.10']))
		event.connection.send(msg)
		log.debug("Flow rule for ICMP traffic for destination 10.0.2.10 added at cs (s5)")

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.match.nw_proto = 1
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = '10.0.4.10'
		msg.actions.append(of.ofp_action_dl_addr.set_src("00:00:00:00:00:05"))
		msg.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac['10.0.4.10']))
		msg.actions.append(of.ofp_action_output(port = ip_to_cs_port['10.0.4.10']))
		event.connection.send(msg)
		log.debug("Flow rule for ICMP traffic for destination 10.0.4.10 added at cs (s5)")

		#The next 4 rules are for allowing IP traffic from h4 (nw_src = 10.0.2.10)
		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.match.nw_proto = 6 #nw_proto for IPv4 packets
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = '10.0.1.10'
		msg.match.nw_src = '10.0.2.10'
		msg.actions.append(of.ofp_action_dl_addr.set_src("00:00:00:00:00:05"))
		msg.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac['10.0.1.10']))
		msg.actions.append(of.ofp_action_output(port = ip_to_cs_port['10.0.1.10']))
		event.connection.send(msg)
		log.debug("Flow rule for IP traffic from 10.0.2.10 to 10.0.1.10 added at cs (s5)")

		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.match.nw_proto = 6
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = '10.0.1.20'
		msg.match.nw_src = '10.0.2.10'
		msg.actions.append(of.ofp_action_dl_addr.set_src("00:00:00:00:00:05"))
		msg.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac['10.0.1.20']))
		msg.actions.append(of.ofp_action_output(port = ip_to_cs_port['10.0.1.20']))
		event.connection.send(msg)
		log.debug("Flow rule for IP traffic from 10.0.2.10 to 10.0.1.20 added at cs (s5)")

		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.match.nw_proto = 6
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = '10.0.1.30'
		msg.match.nw_src = '10.0.2.10'
		msg.actions.append(of.ofp_action_dl_addr.set_src("00:00:00:00:00:05"))
		msg.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac['10.0.1.30']))
		msg.actions.append(of.ofp_action_output(port = ip_to_cs_port['10.0.1.30']))
		event.connection.send(msg)
		log.debug("Flow rule for IP traffic from 10.0.2.10 to 10.0.1.30 added at cs (s5)")

		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.match.nw_proto = 6
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = '10.0.4.10'
		msg.match.nw_src = '10.0.2.10'
		msg.actions.append(of.ofp_action_dl_addr.set_src("00:00:00:00:00:05"))
		msg.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac['10.0.4.10']))
		msg.actions.append(of.ofp_action_output(port = ip_to_cs_port['10.0.4.10']))
		event.connection.send(msg)
		log.debug("Flow rule for IP traffic from 10.0.2.10 to 10.0.4.10 added at cs (s5)")

		#The next 4 rules are for dropping IP traffic from all other sources (h1, h2, h3, SERVER)
		#These rules doesnt have any Action specified. That means Drop action.
		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.match.nw_proto = 6
		msg.match.dl_type = 0x0800
		msg.match.nw_src = '10.0.1.10'
		event.connection.send(msg)
		log.debug("Flow rule for dropping IP traffic from 10.0.1.10 added at cs (s5)")

		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.match.nw_proto = 6
		msg.match.dl_type = 0x0800
		msg.match.nw_src = '10.0.1.20'
		event.connection.send(msg)
		log.debug("Flow rule for dropping IP traffic from 10.0.1.20 added at cs (s5)")

		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.match.nw_proto = 6
		msg.match.dl_type = 0x0800
		msg.match.nw_src = '10.0.1.30'
		event.connection.send(msg)
		log.debug("Flow rule for dropping IP traffic from 10.0.1.30 added at cs (s5)")
		
		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.match.nw_proto = 6
		msg.match.dl_type = 0x0800
		msg.match.nw_src = '10.0.4.10'
		event.connection.send(msg)
		log.debug("Flow rule for dropping IP traffic from 10.0.4.10 added at cs (s5)")


'''
handle packetIn : 
Fired when the controller receives an OpenFlow packet-in messagefrom a switch, 
which indicates that a packet arriving at a switch port has either failed to match all entries in the table, 
or the matching entry included an action specifying to send the packet to the controller.
'''
def _handle_PacketIn(event):
	global mac_to_port
	dpid = event.connection.dpid
	inport = event.port
	packet = event.parsed
	packet_in = event.ofp 
	if not packet.parsed:
		log.warning("%i %i ignoring unparsed packet", dpid, inport)	
	#dpid=5 for the switch cs(s5)
	#All the IP matching rules are already added in _handle_ConnectionUp (proactive rule installation)
	#The firewall should allow ARP traffic through cs.
	#So, ARP requests need to be handled at the controller in _handle_PacketIn
	if(dpid==5):
		if packet.type == pkt.ethernet.ARP_TYPE:
			if packet.payload.opcode == pkt.arp.REQUEST:
				#If the packet is an ARP request, construct an ARP reply and send
				log.debug("ARP request received at switch cs (s5)")
				arp_reply = pkt.arp()
				#Since we are sending the reply to a request, we need to reverse the source and destination
				arp_reply.hwsrc = packet.dst #hwsrc : MAC address of source
				arp_reply.hwdst = packet.src #hwdst : MAC address of destination
				arp_reply.opcode = pkt.arp.REPLY
				arp_reply.protosrc = packet.payload.protodst #protosrc : IP address of source
				arp_reply.protodst = packet.payload.protosrc #protodst : IP address of destination
				#The created ARP packet is added as a payload to an ethernet frame
				ether = pkt.ethernet()
				ether.type = pkt.ethernet.ARP_TYPE
				ether.dst = packet.src
				ether.src = packet.dst
				ether.payload = arp_reply
				msg = of.ofp_packet_out()
				msg.data = ether.pack()
				action = of.ofp_action_output(port = packet_in.in_port)
				msg.actions.append(action)
				event.connection.send(msg)
				log.debug("ARP reply sent")
	#Rest of the switches needs to behave as a learning switch
	else:
		#We need to fill up the mac_to_port data structure as new packets come in
		#If a packet from a particular source comes to switch through a particular port, we know that in the future, if we want to reach that particular source in the future, we can forward to this port
		#Store this information in mac_to_port if its not already there
		if packet.src not in mac_to_port[dpid]:
			mac_to_port[dpid][packet.src] = event.ofp.in_port
		#If the packet's destination mac address is there in the inner dictionary corresponding to this switch, add flow rule to forward the packet to the port in the dictionary
		if packet.dst in mac_to_port[dpid]:
			#flow_mod is for adding the flow rule
			msg = of.ofp_flow_mod()
			msg.match.dl_dst = packet.dst
			msg.actions.append(of.ofp_action_output(port=mac_to_port[dpid][packet.dst]))
			msg.flags=of.OFPFF_SEND_FLOW_REM
			event.connection.send(msg)
			#The following lines are needed because the packet that causes the flow rule to be installed doesnt actually follow the flow rules
			#Only the subsequent packets follow the flow rules
			#So in order for the first packet to not be dropped, the controller needs to explicitly the packet_out for this packet to the same output port that the flow rule was installed
			msg = of.ofp_packet_out(data=event.ofp)
			msg.actions.append(of.ofp_action_output(port=mac_to_port[dpid][packet.dst]))
			event.connection.send(msg)
		#If the packet's destination mac address is not there in the inner dictionary corresponding to this switch, we just flood the packet
		else:
			msg = of.ofp_packet_out(data=event.ofp)
			msg.actions.append(of.ofp_action_output(port=of.OFPP_ALL))
			event.connection.send(msg)
	
		

'''
launch :
Its the main method
'''			
def launch():
	core.openflow.addListenerByName("ConnectionUp",_handle_ConnectionUp)
	core.openflow.addListenerByName("PacketIn",_handle_PacketIn)