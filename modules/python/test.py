

from vcode import generateHMAC
from datagramtalk import datagramTalkMessage


message = datagramTalkMessage( "" )
message.protocol = "iotp2p.ran"
message.protocol_version = "0.0"
message.statement = "MSG"
message.parameters['from'] = "node_a@example.com"
message.parameters['to'] = "node_b@example.com"
message.parameters['vc_ver'] = "0"
message.parameters['vc_nonce'] = "123"
message.parameters['message'] = "Hello world!"
message.toRaw()

print generateHMAC("MTAxOGEwZWQwYjI1Njk1ZjM1N2QwZDQ4OWUwMTFhNDQ1ZGIxZjc3NGUwYTU4YzNkM2ZkYjk5NDhlMjViOGYzNQ==", message)
    
    
    
    
    
    
    