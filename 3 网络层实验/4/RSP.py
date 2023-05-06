from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import arp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import ether_types
from ryu.lib import mac, ip
from ryu.topology import event
from collections import defaultdict
import random


class ProjectController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProjectController, self).__init__(*args, **kwargs)
        self.datapath_list = {}
        self.switches = []
        self.adjacency = defaultdict(dict)
        self.hosts = {'10.0.0.1': (1, 1), '10.0.0.2': (1, 2), '10.0.0.3': (2, 1), '10.0.0.4': (2, 2),
                      '10.0.0.5': (3, 1), '10.0.0.6': (3, 2), '10.0.0.7': (4, 1), '10.0.0.8': (4, 2),
                      '10.0.0.9': (5, 1), '10.0.0.10': (5, 2), '10.0.0.11': (6, 1), '10.0.0.12': (6, 2),
                      '10.0.0.13': (7, 1), '10.0.0.14': (7, 2), '10.0.0.15': (8, 1), '10.0.0.16': (8, 2)}
        self.father={1:(9,10),2:(9,10),3:(11,12),4:(11,12),5:(13,14),6:(13,14),7:(15,16),8:(15,16),9:(17,18),10:(19,20),11:(17,18),12:(19,20),13:(17,18),14:(19,20),15:(17,18),16:(19,20)}
        self.ip_son={
            9:{'10.0.0.1':1,'10.0.0.2':1,'10.0.0.3':2,'10.0.0.4':2},
            10:{'10.0.0.1':1,'10.0.0.2':1,'10.0.0.3':2,'10.0.0.4':2},
            11:{'10.0.0.5':3,'10.0.0.6':3,'10.0.0.7':4,'10.0.0.8':4},
            12:{'10.0.0.5':3,'10.0.0.6':3,'10.0.0.7':4,'10.0.0.8':4},
            13:{'10.0.0.9':5,'10.0.0.10':5,'10.0.0.11':6,'10.0.0.12':6},
            14:{'10.0.0.9':5,'10.0.0.10':5,'10.0.0.11':6,'10.0.0.12':6},
            15:{'10.0.0.13':7,'10.0.0.14':7,'10.0.0.15':8,'10.0.0.16':8},
            16:{'10.0.0.13':7,'10.0.0.14':7,'10.0.0.15':8,'10.0.0.16':8},
            17:{'10.0.0.1':9,'10.0.0.2':9,'10.0.0.3':9,'10.0.0.4':9,'10.0.0.5':11,'10.0.0.6':11,'10.0.0.7':11,'10.0.0.8':11,'10.0.0.9':13,'10.0.0.10':13,'10.0.0.11':13,'10.0.0.12':13,'10.0.0.13':15,'10.0.0.14':15,'10.0.0.15':15,'10.0.0.16':15},
            18:{'10.0.0.1':9,'10.0.0.2':9,'10.0.0.3':9,'10.0.0.4':9,'10.0.0.5':11,'10.0.0.6':11,'10.0.0.7':11,'10.0.0.8':11,'10.0.0.9':13,'10.0.0.10':13,'10.0.0.11':13,'10.0.0.12':13,'10.0.0.13':15,'10.0.0.14':15,'10.0.0.15':15,'10.0.0.16':15},
            19:{'10.0.0.1':10,'10.0.0.2':10,'10.0.0.3':10,'10.0.0.4':10,'10.0.0.5':12,'10.0.0.6':12,'10.0.0.7':12,'10.0.0.8':12,'10.0.0.9':14,'10.0.0.10':14,'10.0.0.11':14,'10.0.0.12':14,'10.0.0.13':16,'10.0.0.14':16,'10.0.0.15':16,'10.0.0.16':16},
            20:{'10.0.0.1':10,'10.0.0.2': 10,'10.0.0.3': 10,'10.0.0.4': 10,'10.0.0.5': 12,'10.0.0.6': 12,'10.0.0.7': 12,'10.0.0.8': 12,'10.0.0.9': 14,'10.0.0.10': 14,'10.0.0.11': 14,'10.0.0.12': 14,'10.0.0.13': 16,'10.0.0.14': 16,'10.0.0.15': 16,'10.0.0.16': 16},
        }
        self.path=defaultdict(list)
        self.key=[('10.0.0.12','10.0.0.16'),('10.0.0.12','10.0.0.1')] #学号：20307130112
        random.seed(998244353)


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    def ip2num(self,s:str):
        s=s.split('.')[-1]
        return int(s)

    def cal_path(self, src, dst):
        dpid=self.hosts[src][0]
        while True:
            self.path[(src,dst)].append(dpid)
            if(1 <= dpid and dpid <= 8):
                if (self.hosts[dst][0] == dpid):
                    break
                else:
                    dpid=self.father[dpid][random.randint(0,1)]
            else:
                if (dst in self.ip_son[dpid]):
                    dpid=self.ip_son[dpid][dst]
                else:
                    dpid=self.father[dpid][random.randint(0,1)]
        if (src,dst) in self.key:
            self.print_path((src,dst))

    def get_nxt(self,dpid,src,dst):
        if (src,dst) not in self.path:
            self.cal_path(src,dst)
        now_path=self.path[(src,dst)]
        idx=0
        # print(self.adjacency[5])
        for i in range(len(now_path)):
            if now_path[i]==dpid:
                if i==len(now_path)-1:
                    return self.hosts[dst][1]
                else:
                    idx=i
                    return self.adjacency[dpid][now_path[i+1]]

    def print_path(self, key):
        print("h%d ->" % (self.ip2num(key[0])), end=" ")
        for i in self.path[key]:
            print("s%d ->" % (i), end=" ")
        print("h%d" % (self.ip2num(key[1])))

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def _switch_features_handler(self, ev):
        print("switch_features_handler is called")
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg                   #switch送来的事件ev,ev.msg 是表示packet_in数据结构的一个对象
        datapath = msg.datapath        #msg.datapath是switch Datapath的一个对象，是哪个switch发来的消息
        ofproto = datapath.ofproto     #协商的版本
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet) # 获取二层包头信息
        in_port = msg.match['in_port']
        if eth.ethertype == ether_types.ETH_TYPE_LLDP: # ignore lldp packet
            return
        src=None
        dst=None
        dpid=datapath.id
        match=None
        parser = datapath.ofproto_parser
        if eth.ethertype==ether_types.ETH_TYPE_IP:
            _ipv4=pkt.get_protocol(ipv4.ipv4)
            src=_ipv4.src
            dst=_ipv4.dst
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, in_port=in_port, ipv4_src=src, ipv4_dst=dst)
        elif eth.ethertype==ether_types.ETH_TYPE_ARP:
            arp_pkt=pkt.get_protocol(arp.arp)
            src=arp_pkt.src_ip
            dst=arp_pkt.dst_ip
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP, in_port=in_port, arp_spa=src, arp_tpa=dst)
        else:
            return
        out_port=self.get_nxt(dpid,src,dst)
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)] 
        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            self.add_flow(datapath,1,match,actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:  # 还得把包送往该去的端口
            data = msg.data
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=data)
        datapath.send_msg(out)



    @set_ev_cls(event.EventSwitchEnter)
    def switch_enter_handler(self, ev):
        print(ev)
        switch = ev.switch.dp
        if switch.id not in self.switches:
            self.switches.append(switch.id)
            self.datapath_list[switch.id] = switch


    @set_ev_cls(event.EventSwitchLeave, MAIN_DISPATCHER)
    def switch_leave_handler(self, ev):
        print(ev)
        switch = ev.switch.dp.id
        # print(switch)
        # print(self.adjacency)
        if switch in self.switches:
            self.switches.remove(switch)
            del self.datapath_list[switch]
            del self.adjacency[switch]


    #get adjacency matrix of fattree
    @set_ev_cls(event.EventLinkAdd, MAIN_DISPATCHER)
    def link_add_handler(self, ev):
        s1 = ev.link.src
        s2 = ev.link.dst
        self.adjacency[s1.dpid][s2.dpid] = s1.port_no
        self.adjacency[s2.dpid][s1.dpid] = s2.port_no

    @set_ev_cls(event.EventLinkDelete, MAIN_DISPATCHER)
    def link_delete_handler(self, ev):
        # s1 = ev.link.src
        # s2 = ev.link.dst
        # # Exception handling if switch already deleted
        # try:
        #     del self.adjacency[s1.dpid][s2.dpid]
        #     del self.adjacency[s2.dpid][s1.dpid]
        # except KeyError:
        #     pass
        pass