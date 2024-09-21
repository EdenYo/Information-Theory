import requests
import time


def run_length_encode(data):
    """Encodes the input data using Run-Length Encoding and returns two lists: characters and their frequencies."""
    if not data:
        return [], []

    chars = []
    frequencies = []
    count = 1

    for i in range(1, len(data)):
        if data[i] == data[i - 1]:
            count += 1
        else:
            chars.append(data[i - 1])
            frequencies.append(count)
            count = 1
    chars.append(data[-1])  # Append the last run
    frequencies.append(count)

    return chars, frequencies


def prepare_frequencies_for_storage(frequencies):
    """Prepares the frequencies for storage, separating multi-digit numbers with commas."""
    freq_str = []

    for freq in frequencies:
        if freq >= 10:  # If frequency is two or more digits, separate it with a comma
            freq_str.append(f',{freq},')
        else:
            freq_str.append(str(freq))  # Single-digit frequencies stored without a comma

    return ''.join(freq_str)


def run_length_decode(chars, frequency_string):
    """Decodes the input characters and their frequencies back to the original data."""
    decoded = []
    frequency_index = 0

    for i in range(len(chars)):
        if frequency_string[frequency_index] != ',':
            decoded.append(chars[i] * int(frequency_string[frequency_index]))
            frequency_index += 1
        else:
            frequency_index += 1
            decoded.append(chars[i] * int(frequency_string[frequency_index] + frequency_string[frequency_index + 1]))
            frequency_index += 3

    return ''.join(decoded)


if __name__ == '__main__':
    input_file_url = 'https://raw.githubusercontent.com/kzjeef/algs4/master/burrows-wheelers/testfile/dickens.txt'
    response = requests.get(input_file_url)

    if response.status_code == 200:
        input_data = response.text

        # Compression
        compress_start_time = time.time()
        chars, frequencies = run_length_encode(input_data)

        # Prepare frequencies for storage
        frequency_string = prepare_frequencies_for_storage(frequencies)

        # Save chars and frequencies in separate files
        with open("RLE_chars.txt", 'w', encoding="utf-8") as file:
            file.write(''.join(chars))

        with open("RLE_frequencies.txt", 'w', encoding="utf-8") as file:
            file.write(frequency_string)

        print("---compress %s seconds ---" % (time.time() - compress_start_time))

        # Decompression
        decompress_start_time = time.time()

        # Read the characters and frequencies from the files
        with open("RLE_chars.txt", 'r', encoding="utf-8") as file:
            chars = list(file.read())

        with open("RLE_frequencies.txt", 'r', encoding="utf-8") as file:
            frequency_string = file.read()

        decompressed_data = run_length_decode(chars, frequency_string)
        with open("RLE_decompressed.txt", 'w', encoding="utf-8") as file:
            file.write(decompressed_data)

        print("---decompress %s seconds ---" % (time.time() - decompress_start_time))
