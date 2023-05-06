import pickle
def pack(type,seq,ack,data):
    dict={}
    dict['type']=type
    dict['seq']=seq
    dict['ack']=ack
    dict['data']=data
    return pickle.dumps(dict)

def unpack(ptk):
    dict=pickle.loads(ptk)
    return dict