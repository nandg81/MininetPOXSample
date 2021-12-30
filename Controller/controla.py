'''
Roll no : 2021H1030103P
Conroller for question A
'''

from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of

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
handle ConnectionUp :
fired in response to the establishment of a new control channel with a switch.
'''
def _handle_ConnectionUp(event):
	global mac_to_port
	#initialise the outer dictionary with key values as switch dpids as the connection with switch gets established and with empty values
	mac_to_port[event.connection.dpid]={}
	print("Switch ",event.connection.dpid)
	print(dpid_to_str(event.connection.dpid))
	for swprt in event.connection.features.ports:
		print(swprt.name)

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
	if not packet.parsed:
		log.warning("%i %i ignoring unparsed packet", dpid, inport)
	
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