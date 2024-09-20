import requests
import time


def run_length_encode(data):
    """Encodes the input data using Run-Length Encoding."""
    if not data:
        return ""

    encoded = []
    count = 1
    for i in range(1, len(data)):
        if data[i] == data[i - 1]:
            count += 1
        else:
            encoded.append(f"{data[i - 1]}{count}")
            count = 1
    encoded.append(f"{data[-1]}{count}")  # Append the last run
    return ''.join(encoded)


def run_length_decode(encoded_data):
    """Decodes the input data using Run-Length Encoding."""
    decoded = []
    count = "1"

    for char in encoded_data:
        if char.isdigit():
            count += char  # Build the count string
        else:
            decoded.append(char * int(count))  # Repeat the character count times
            count = ""

    decoded_text = ''
    chunk_size = 8000
    for i in range(0, len(decoded), chunk_size):
        chunk = decoded[i:i+chunk_size]
        decoded_text += ''.join(chunk)

    return decoded_text


if __name__ == '__main__':
    input_file_url = 'https://raw.githubusercontent.com/kzjeef/algs4/master/burrows-wheelers/testfile/dickens.txt'
    response = requests.get(input_file_url)

    if response.status_code == 200:
        input_data = response.text

        # Compression
        compress_start_time = time.time()
        compressed_data = run_length_encode(input_data)
        with open("RLE_compressed.txt", 'w', encoding="utf-8") as file:
            file.write(compressed_data)
        print("---compress %s seconds ---" % (time.time() - compress_start_time))

        # Decompression
        decompress_start_time = time.time()
        decompressed_data = run_length_decode(compressed_data)
        with open("RLE_decompressed.txt", 'w', encoding="utf-8") as file:
            file.write(decompressed_data)
        print("---decompress %s seconds ---" % (time.time() - decompress_start_time))