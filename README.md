# stringobf
Encodes 7-bit character strings into dependent chains of noise. (And decodes them ... of course.)

The encoding of a 7-bit character starts with a given (random) 128-byte 'source' block. A random 127-byte 'indices' block is generated, which selects a byte from the source block, by a 7-bit index. Another random 127 bits are generated, which each represent an operation to perform (0 for addition, 1 for multiplication). Each selected source byte is paired in sequence with its associated operation into 127 partial operations, requiring an additional byte argument to reduce each 'partial'. A random 'seed' byte is generated and applied to the first partial, and stored into a 'result', and trimmed to an 8-bit field. This process repeats with the previous result applied to each partial in sequence, accumulating back into the result field. After all partials have been reduced, the result is checked to see if it is equal to the character to be encoded. If so, a tuple containing the seed, operations, and indices are returned. Otherwise, the entire process repeats in search of a tuple that encodes the character.

This process repeats 64 times on average to find a suitable tuple. (That is, half of 128 possible result states.)

The returned operations and indices are combined pairwise by setting the high bit of the indices' byte to the encoded operation bit. These 127 bytes are prefixed with the seed byte, resulting in a 128 byte 'packed' block. The packed block is then appended to the source block to represent the encoded character.

Strings of characters are encoded by 'chaining' together packed blocks of characters. The source of the next encoded character is derived by hashing the block of its predecessor. As a consequence, a string of characters is encoded into a final chain of (1 + n) * 128 bytes, where n is the length of the original string. That is, some random source block plus each packed block.

Chained strings are decoded by performing the process in reverse.

This method of encoding can be used to obfuscate strings in a manner which requires sequential evaluation to decode. Multiple printable strings can be encoded by appending a null byte (c-style), delimiting each string.
