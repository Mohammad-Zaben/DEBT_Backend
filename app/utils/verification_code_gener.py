import hashlib
import hmac
import time
import struct

def generate_verification_code(secret_key):
    key = bytes.fromhex(secret_key)
    
    current_time = int(time.time())
    time_counter = current_time // 60  
    
    time_bytes = struct.pack(">Q", time_counter)
    
    hmac_hash = hmac.new(key, time_bytes, hashlib.sha1).digest()
    
    offset = hmac_hash[-1] & 0xF
    binary_code = struct.unpack(">I", hmac_hash[offset:offset + 4])[0]
    binary_code = binary_code & 0x7FFFFFFF
    
    otp = binary_code % 1000000
    print(f"Generated OTP: {otp:06d}")
    return f"{otp:06d}"

