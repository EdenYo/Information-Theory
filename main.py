import contextlib
from datetime import datetime
import filecmp
import arithmeticcoding
import ppm_model



def main():
    input_file = "input.txt"
    compressed_file = "compressed_file.bin"
    decompressed_file = "decompressed_file.txt"

    print("Encoding:")
    print(datetime.now().strftime("%H:%M:%S"))
    # File compression
    with open(input_file, "rb") as inp, contextlib.closing(ppm_model.BitStream(open(compressed_file, "wb"))) as bit_file:
        compress(inp, bit_file)

    print("\nDecoding:")
    print(datetime.now().strftime("%H:%M:%S"))
    with open(compressed_file, "rb") as comp_file, open(decompressed_file, "wb") as decomp_file:
        bitin = ppm_model.BitStream(comp_file, "read")
        decompress(bitin, decomp_file)

    print("\nDone:")
    print(datetime.now().strftime("%H:%M:%S"))

    are_identical = filecmp.cmp(input_file, decompressed_file)
    print(f"\n\nValidation: Files are {'identical' if are_identical else 'different'}")


def compress(inp, bit_file):
    # Initialize the arithmetic encoder with a precision of 32 bits and output stream bit_file
    encode = arithmeticcoding.ArithmeticEncoder(32, bit_file)
    model = ppm_model.PpmModel(3, 257, 256)
    history = []    # Track context symbols

    while True:
        symbol = inp.read(1)         # Read and encode one byte
        if len(symbol) == 0:
            break
        symbol = symbol[0]
        encode_symbol(model, history, symbol, encode)
        model.increment_contexts(history, symbol)

        if model.model_order >= 1:
            # Dropping oldest symbol (if necessary)
            if len(history) == model.model_order:
                history.pop()
            history.insert(0, symbol)   # Add the new symbol to the beginning of the history

    encode_symbol(model, history, 256, encode)  # EOF
    encode.finish()

def decompress(bitin, out):
    # Initialize the arithmetic decoder with a precision of 32 bits and input stream bitin
    decode = arithmeticcoding.ArithmeticDecoder(32, bitin)
    model = ppm_model.PpmModel(3, 257, 256)
    history = []
    EOF_SYM = 256

    while True:
        symbol = decode_symbol(decode, model, history)     # Decode and write one byte
        if symbol == EOF_SYM:
            break
        out.write(bytes((symbol,)))
        model.increment_contexts(history, symbol)

        if model.model_order >= 1:
            if len(history) == model.model_order:
                history.pop()   # Remove the oldest symbol from history
            history.insert(0, symbol)

def encode_symbol(model, history, symbol, enc):
    # Use the highest order context with a non-zero frequency
    # If symbol 256 appears, escape to a lower order or signal EOF at order -1
    for order in reversed(range(len(history) + 1)):
        ctx = model.root_context
        for sym in history[: order]:
            assert ctx.subcontexts is not None
            ctx = ctx.subcontexts[sym]
            if ctx is None:
                break
        else:
            if symbol != 256 and ctx.frequencies.get(symbol) > 0:
                enc.write(ctx.frequencies, symbol)
                return

            enc.write(ctx.frequencies, 256)

    enc.write(model.order_minus1_freqs, symbol)

def decode_symbol(dec, model, history):
    # Ensure valid input: order must be >= -1, escape symbol must be within symbol limit
    for order in reversed(range(len(history) + 1)):
        ctx = model.root_context
        for sym in history[: order]:
            assert ctx.subcontexts is not None
            ctx = ctx.subcontexts[sym]
            if ctx is None:
                break
        else:
            symbol = dec.read(ctx.frequencies)
            if symbol < 256:
                return symbol
    return dec.read(model.order_minus1_freqs)

if __name__ == "__main__":
    main()

