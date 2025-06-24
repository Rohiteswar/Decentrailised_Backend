from eth_account.messages import encode_defunct
from eth_account import Account
import re

def is_valid_ethereum_address(address):
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))

def verify_signature(message, signature, address):
    try:
        msg_encoded = encode_defunct(text=message)
        recovered = Account.recover_message(msg_encoded, signature=signature)
        return recovered.lower() == address.lower()
    except Exception:
        return False