from helper.helper import little_endian_to_int, hash256, decode_base58
from crypto.Signature import PrivateKey




secret_Abel = little_endian_to_int(hash256(b'abelyang@astri.org'))
private_key_Abel = PrivateKey(secret=secret_Abel)
# private_key: cUz2mXMT2jyqdwXuFeZgy71tvF96vnvAmH8KvtsMdzhY2AtrJUJv
addr_Abel = private_key_Abel.point.address(testnet=True)
# my_addr = 'n4kJxHoZC9uTjfYAmeXSnHP9ss6YqiQja8'
h160_Abel = decode_base58(addr_Abel)
print("Abel's private key is: ", private_key_Abel)
print("Abel's address is: ", addr_Abel)


secret_Alice = little_endian_to_int(hash256(b'Alice'))
private_key_Alice = PrivateKey(secret=secret_Alice)
# private_key: cUz2mXMT2jyqdwXuFeZgy71tvF96vnvAmH8KvtsMdzhY2AtrJUJv
addr_Alice = private_key_Alice.point.address(testnet=True)
# my_addr = 'n4kJxHoZC9uTjfYAmeXSnHP9ss6YqiQja8'
h160_Alice = decode_base58(addr_Alice)
print("Alice's private key is: ", private_key_Alice)
print("Alice's address is: ", addr_Alice)

secret_Bob = little_endian_to_int(hash256(b'Bob'))
private_key_Bob = PrivateKey(secret=secret_Bob)
# private_key: cUz2mXMT2jyqdwXuFeZgy71tvF96vnvAmH8KvtsMdzhY2AtrJUJv
addr_Bob = private_key_Bob.point.address(testnet=True)
# my_addr = 'n4kJxHoZC9uTjfYAmeXSnHP9ss6YqiQja8'
h160_Bob = decode_base58(addr_Bob)
print("Bob's private key is: ", private_key_Bob)
print("Bob's address is: ", addr_Bob)
