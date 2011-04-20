'General purpose tools'
import hashlib
import random


alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
secret = ''


def hash_string(string): 
    'Compute the hash of the string'
    return hashlib.sha256(string + secret).digest()


def make_random_string(length):
    'Return a random string of a specified length'
    return ''.join(random.choice(alphabet) for x in xrange(length))


def make_random_unique_string(length, is_unique):
    """
    Return a random unique string given a function that
    checks whether the string is unique
    """
    # Initialize
    iterationCount = 0
    permutationCount = len(alphabet) ** length
    while iterationCount < permutationCount:
        # Make randomID
        randomID = make_random_string(length)
        iterationCount += 1
        # If our randomID is unique, return it
        if is_unique(randomID):
            return randomID
    # Raise exception if we have no more permutations left
    raise RuntimeError('Could not create a unique string')
