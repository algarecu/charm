from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.crypto.cryptobase import *
from charm.core.math.pairing import hashPair as sha1
from schemes.dabenc.dabe_aw11 import *
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
#from charm.toolbox.pairinggroup import *

debug = False
class HybridABEncMA(ABEncMultiAuth):
    """
    >>> group = PairingGroup('SS512')
    >>> dabe = Dabe(group)

    Setup master authority.
    >>> hyb_abema = HybridABEncMA(dabe, group)
    >>> global_parameters = hyb_abema.setup()
    
	Generate attributes for two different sub-authorities:
    Johns Hopkins University, and Johns Hopkins Medical Institutions.
    >>> jhu_attributes = ['jhu.professor', 'jhu.staff', 'jhu.student']
    >>> jhmi_attributes = ['jhmi.doctor', 'jhmi.nurse', 'jhmi.staff', 'jhmi.researcher']

    Johns Hopkins sub-authorities master key.
    >>> (jhu_secret_key, jhu_public_key) = hyb_abema.authsetup(global_parameters, jhu_attributes)

    JHMI sub-authorities master key
    >>> (jhmi_secret_key, jhmi_public_key) = hyb_abema.authsetup(global_parameters, jhmi_attributes)
    
    To encrypt messages we need all of the authorities' public keys.
    >>> allAuth_public_key = {}; 
    >>> allAuth_public_key.update(jhu_public_key); 
    >>> allAuth_public_key.update(jhmi_public_key)
    
    An example user, Bob, who is both a professor at JHU and a researcher at JHMI.
    >>> ID = "20110615 bob@gmail.com cryptokey"
    >>> secrets_keys = {}
    >>> hyb_abema.keygen(global_parameters, jhu_secret_key,'jhu.professor', ID, secrets_keys)
    >>> hyb_abema.keygen(global_parameters, jhmi_secret_key,'jhmi.researcher', ID, secrets_keys)
    
    Encrypt a message to anyone who is both a profesor at JHU and a researcher at JHMI.
    >>> msg = b'Hello World, I am a sensitive record!'
    >>> policy_str = "(jhmi.doctor or (jhmi.researcher and jhu.professor))"
    >>> cipher_text = hyb_abema.encrypt(allAuth_public_key, global_parameters, msg, policy_str)    

    >>> hyb_abema.decrypt(global_parameters, secrets_keys, cipher_text)
    b'Hello World, I am a sensitive record!'
    """
    def __init__(self, scheme, groupObj):
        global abencma, group
        # check properties (TODO)
        abencma = scheme
        group = groupObj

    def setup(self):
        return abencma.setup()
    
    def authsetup(self, gp, attributes):
        return abencma.authsetup(gp, attributes)
    
    def keygen(self, gp, sk, i, gid, pkey):
        return abencma.keygen(gp, sk, i, gid, pkey)

    def encrypt(self, pk, gp, M, policy_str):
        if type(M) != str and type(policy_str) != str: raise "message and policy not right type!"        
#        if type(M) != bytes and type(policy_str) != str: raise "message and policy not right type!"        
        key = group.random(GT)
        c1 = abencma.encrypt(pk, gp, key, policy_str)
        # instantiate a symmetric enc scheme from this key
        cipher = AuthenticatedCryptoAbstraction(sha1(key)) 
        c2 = cipher.encrypt(M)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, gp, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = abencma.decrypt(gp, sk, c1)
        cipher = AuthenticatedCryptoAbstraction(sha1(key))
        return cipher.decrypt(c2)
        
