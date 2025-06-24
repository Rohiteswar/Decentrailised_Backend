from eth_account import Account
from eth_account.messages import encode_defunct
import re

def is_valid_ethereum_address(address):
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))

def verify_signature(message, signature, address):
    try:
        message_encoded = encode_defunct(text=message)
        recovered_address = Account.recover_message(message_encoded, signature=signature)
        return recovered_address.lower() == address.lower()
    except:
        return False
