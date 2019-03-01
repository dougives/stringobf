#!/usr/bin/python3
import os
from operator import add, mul
import sys
from functools import reduce, partial
from itertools import starmap
import gzip


def xor_shift_star(x, s):
    x += s + 257
    x *= 0x2aaaaaab
    x ^= x >> 12
    x ^= x << 25
    x ^= x >> 27
    return (x * 0x2eb2563693) & 255

def search_for_char(source, c, minlen=16, maxlen=32):
    assert len(source) <= 256
    #ops = [ add, mul ]
    #result = reduce(lambda x, f: f(x), codons) & 127
    while True:
        indices = [ r % (len(source)-1) for r in os.urandom(maxlen) ]
        ops = [ add if r & 1 else mul for r in os.urandom(maxlen) ]
        partials = list(starmap(partial, zip(ops, [ source[i] for i in indices ])))
        seed = os.urandom(1)[0]
        result = partials[0](seed)
        for i in range(1, len(partials)):
            #sys.stdout.write(f'.')
            #sys.stdout.flush()
            result = partials[i](result) & 255
            if chr(result) == c:
                if i < minlen - 1:
                    #sys.stdout.write(f'*')
                    #sys.stdout.flush()
                    continue
                sys.stdout.write(f'+')
                sys.stdout.flush()
                return (seed, ops[:i+1], indices[:i+1], result)
            if result == 0:
                #sys.stdout.write(f'!')
                #sys.stdout.flush()
                break

def search_for_string(source, s, minlen=16, maxlen=32):
    return [ search_for_char(source, c, minlen, maxlen) for c in s ]

def search_for_packed_char(source, c, length=128):
    assert len(source) == 128
    tail_length = length - 1
    seed, ops, indicies, result = search_for_char(source, c, tail_length, tail_length)
    return bytes([ seed ] + [ (1<<7 if ops[i] == add else 0) | indicies[i] for i in range(tail_length) ])

def search_for_chained_string(source, s):
    assert len(source) == 128
    result = bytes()
    for c in s:
        cres = search_for_packed_char(source, c)
        result += cres
        source = [ xor_shift_star(x, ord(c)) for x in cres ]
    return result

def search_for_chained_strings(source, *sargs):
    assert len(source) == 128
    s = '\0'.join(sargs) + '\0'
    return search_for_chained_string(source, s)

def search_for_packed_string(source, s):
    assert len(source) == 128
    return list(reduce(add, ( search_for_packed_char(source, c) for c in s )))

def search_for_packed_strings(source, *sargs):
    assert len(source) == 128
    s = '\0'.join(sargs) + '\0'
    return search_for_packed_string(source, s)

def decode_chained_strings(source, blob):
    assert len(source) == 128
    assert len(blob) % 128 == 0
    def decode_block(block):
        seed = block[0]
        tail = block[1:]
        for x in tail:
            op = add if x>>7 else mul
            sel = source[x & 0x7f]
            seed = op(seed, sel)
            seed &= 255
        return seed
    sres = ''
    for i in range(0, len(blob), 128):
        block = blob[i:i+128]
        c = decode_block(block)
        if not c:
            yield sres
            if i >= len(blob) - 128:
                break
            sres = ''
            source = [ xor_shift_star(x, c) for x in block ]
            continue
        sres += chr(c)
        source = [ xor_shift_star(x, c) for x in block ]
        
def main():
    strings = [ 
        'test', 
        '123', 
        'check', 
        'mary had a little lamb', 
        'whose fleece was white as snow',
        'everywhere that mary went',
        'the lamb was sure to go',
        'it made the children laugh and play',
        'to see a lamb at school' ]
    source = os.urandom(128)

    #print(xor_shift_star(0, 1))
    plain_length = len('\0'.join(strings) + '\0')
    print(plain_length)
    result = search_for_chained_strings(source, *strings)
    print()
    coded_length = len(result)
    print(coded_length) #, ''.join([ f'{y:02x}' for y in result ]))
    print(list(decode_chained_strings(source, result)))
    [ print(f'{seed:02x}', f'{int("".join([ "1" if op == add else "0" for op in ops ]), 2):08x}', ''.join([ f'{y:02x}' for y in indicies ]), chr(result), '\n') for seed, ops, indicies, result in search_for_string(source, strings[0], 32, 32) ]

    return 0


if __name__ == '__main__':
    exit(main())
