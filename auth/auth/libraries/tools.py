"""General purpose tools"""
import random
import string
import hashlib


def make_random_string(length):
    """Return a random string of a specified length"""
    alphabet = string.letters + string.digits
    return ''.join(random.choice(alphabet) for x in xrange(length))


def hash_string(string): 
    """Compute the hash of the string"""
    return hashlib.sha256(string).digest()
