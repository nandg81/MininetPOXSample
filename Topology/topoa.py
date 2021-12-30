'''
Roll no : 2021H1030103P
Topology for question A
'''

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink

def topology():

	net = Mininet(topo=None, link=TCLink, build=False, ipBase='10.0.0.0/8')

	#Specifying the remote controller and its port
	c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1',  protocol='tcp', port=6633)
	
	#Add hosts and switches


	print("Adding hosts")
	h1 = net.addHost('h1')
	h2 = net.addHost('h2')	    	
	h3 = net.addHost('h3')
	h4 = net.addHost('h4')
	server = net.addHost( 'SERVER')

	print("Adding switches")
	s1 = net.addSwitch( 's1',  cls=OVSKernelSwitch )
	s2 = net.addSwitch( 's2',  cls=OVSKernelSwitch )
	s3 = net.addSwitch( 's3',  cls=OVSKernelSwitch )
	s4 = net.addSwitch( 's4',  cls=OVSKernelSwitch )
	cs = net.addSwitch( 's5',  cls=OVSKernelSwitch )

	print("Adding links")
	#Same bandwidth is given for all links
	net.addLink( h1, s1, bw = 50, loss = 0 )
	net.addLink( h2, s2, bw = 50, loss = 0 )
	net.addLink( h3, s3, bw = 50, loss = 0 )
	net.addLink( s1, cs, bw = 50, loss = 0 )   
	net.addLink( s4, cs, bw = 50, loss = 0 )
	net.addLink( h4, cs, bw = 50, loss = 0 )
	net.addLink( s3, cs, bw = 50, loss = 0 )	    	    	
	net.addLink( s2, cs, bw = 50, loss = 0 )
	net.addLink( s4, server, bw = 50, loss = 0 )	    	

	net.build()

	print("Starting controller")
	c0.start()

	s1.start( [c0] )
	s2.start( [c0] )
	s3.start( [c0] )
	s4.start( [c0] )
	cs.start( [c0] )

	print ("*** Running CLI")
	CLI( net )

	print ("*** Stopping network")
	net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()   