'General purpose tools'
import hashlib
import random
import string


alphabet = string.letters + string.digits


def hash_string(string): 
    'Compute the hash of the string'
    return hashlib.sha256(string).digest()


def make_random_string(length):
    'Return a random string of a specified length'
    return ''.join(random.choice(alphabet) for x in xrange(length))


def make_random_unique_string(length, is_unique):
    """
    Return a random unique string given a function that
    checks whether the string is unique
    """
    # Initialize
    numberOfPossibilities = len(letters + numbers) ** length
    iterationCount = 0
    # Loop through possibilities until our randomID is unique
    while iterationCount < numberOfPossibilities:
        # Make randomID
        iterationCount += 1
        randomID = makeRandomString(length)
        # If our randomID is unique, return it
        if not query.filter_by(ticket=randomID).first(): 
            return randomID
