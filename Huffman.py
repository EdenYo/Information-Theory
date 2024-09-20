import heapq
import os
import requests
import time

class HuffmanNode:
    def __init__(self, char, frequency):
        self.char = char
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency


def build_huffman_tree(text):
    frequency = {}
    for char in text:
        if char in frequency:
            frequency[char] += 1
        else:
            frequency[char] = 1

    priority_queue = []
    for char, freq in frequency.items():
        node = HuffmanNode(char, freq)
        heapq.heappush(priority_queue, node)

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)
        merged = HuffmanNode(None, left.frequency + right.frequency)
        merged.left = left
        merged.right = right
        heapq.heappush(priority_queue, merged)

    return priority_queue[0]


def build_huffman_codes(node, current_code="", huffman_codes={}):
    if node is not None:
        if node.char is not None:
            huffman_codes[node.char] = current_code
        build_huffman_codes(node.left, current_code + "0", huffman_codes)
        build_huffman_codes(node.right, current_code + "1", huffman_codes)
    return huffman_codes


def encode_text(text, huffman_codes):
    encoded_text = ""
    for char in text:
        encoded_text += huffman_codes[char]

    # Add padding if necessary
    extra_padding = 8 - len(encoded_text) % 8
    if extra_padding != 8:
        encoded_text += '0' * extra_padding

    # Store the padding information in the first byte
    padded_info = "{0:08b}".format(extra_padding)
    encoded_text = padded_info + encoded_text

    # Convert the binary string to bytes
    byte_array = bytearray()
    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i+8]
        byte_array.append(int(byte, 2))

    return byte_array



def decode_text(encoded_text, huffman_tree):
    decoded_text = ""
    current_node = huffman_tree
    for bit in encoded_text:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
        if current_node.char is not None:
            decoded_text += current_node.char
            current_node = huffman_tree
    return decoded_text


def huffman_compress(input_file, output_file):
    response = requests.get(input_file)
    text = response.text

    huffman_tree = build_huffman_tree(text)
    huffman_codes = build_huffman_codes(huffman_tree)
    encoded_bytes = encode_text(text, huffman_codes)

    with open(output_file, 'wb') as file:
        file.write(bytes(encoded_bytes))

    return huffman_tree


def huffman_decompress(compressed_file, decompressed_file, huffman_tree):
    with open(compressed_file, 'rb') as file:
        byte_data = file.read()

    # Extract padding info from the first byte
    padded_info = byte_data[0]
    extra_padding = int(f"{padded_info:08b}", 2)

    encoded_text = ""
    for byte in byte_data[1:]:
        encoded_text += f"{byte:08b}"

    # Remove the padding from the end of the encoded text
    if extra_padding > 0:
        encoded_text = encoded_text[:-extra_padding]

    decoded_text = decode_text(encoded_text, huffman_tree)

    with open(decompressed_file, 'w', encoding="utf-8") as file:
        file.write(decoded_text)


if __name__ == '__main__':
    input_file = 'https://raw.githubusercontent.com/kzjeef/algs4/master/burrows-wheelers/testfile/dickens.txt'
    compressed_file = "Huffman_compressed.txt"
    decompressed_file = "Huffman_decompressed.txt"

    compress_start_time = time.time()
    huffman_tree = huffman_compress(input_file, compressed_file)
    print("---compress %s seconds ---" % (time.time() - compress_start_time))


    decompress_start_time = time.time()
    huffman_decompress(compressed_file, decompressed_file, huffman_tree)
    print("---decompress %s seconds ---" % (time.time() - decompress_start_time))