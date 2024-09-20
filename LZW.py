import requests
import time


def lzw_compress(text):
    dictionary = {}
    result = []
    current_code = 0
    phrase = ""

    for symbol in text:
        if symbol not in dictionary.keys():
            dictionary[symbol] = current_code
            current_code = current_code + 1

    for symbol in text:
        new_phrase = phrase + symbol
        if new_phrase in dictionary:
            phrase = new_phrase
        else:
            result.append(dictionary[phrase])
            dictionary[new_phrase] = current_code
            current_code += 1
            phrase = symbol

    if phrase in dictionary:
        result.append(dictionary[phrase])

    return result, dictionary


def lzw_decompress(compressed, dictionary):
    reverse_dictionary = {v: k for k, v in dictionary.items()}
    result = ""
    previous_code = compressed[0]
    result += reverse_dictionary[previous_code]

    for code in compressed[1:]:
        if code in reverse_dictionary:
            entry = reverse_dictionary[code]
            result += entry
            new_entry = reverse_dictionary[previous_code] + entry[0]
            reverse_dictionary[len(reverse_dictionary)] = new_entry
            previous_code = code
        else:
            entry = reverse_dictionary[previous_code] + reverse_dictionary[previous_code][0]
            result += entry
            reverse_dictionary[len(reverse_dictionary)] = entry
            previous_code = code

    return result


if __name__ == '__main__':
    #text = "TOBEORNOTTOBEORTOBEORNOT"
    input_file = 'https://raw.githubusercontent.com/kzjeef/algs4/master/burrows-wheelers/testfile/dickens.txt'
    response = requests.get(input_file)
    text = response.text

    compress_start_time = time.time()
    compressed_text, dictionary = lzw_compress(text)
    with open("LZW_compressed.txt", 'w', encoding="utf-8") as file:
        file.write(",".join(map(str, compressed_text)))
    print("---compress %s seconds ---" % (time.time() - compress_start_time))

    decompress_start_time = time.time()
    decompressed_text = lzw_decompress(compressed_text, dictionary)
    with open("LZW_decompressed.txt", 'w', encoding="utf-8") as file:
        file.write(decompressed_text)
    print("---decompress %s seconds ---" % (time.time() - decompress_start_time))
