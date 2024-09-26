import frequencies

class BitStream:

    # Constructs a bit input stream based on the given byte input stream.
    def __init__(self, stream, read_or_write="write"):
        # The underlying byte stream to read from
        self.stream = stream
        # Either in the range [0x00, 0xFF] if bits are available, or -1 if end of stream is reached
        self.currentbyte = 0
        # Number of remaining bits in the current byte, always between 0 and 7 (inclusive)
        self.numbits = 0
        self.read_or_write = read_or_write

    def close(self):
        while self.numbits != 0:
            self.handle_file(0)
        self.stream.close()


    def handle_file(self, b=None):
        if self.read_or_write == "read":
            # Reads a bit from this stream. Returns 0 or 1 if a bit is available, or -1 if
            # the end of stream is reached. The end of stream always occurs on a byte boundary.
            if self.currentbyte == -1:
                return -1
            if self.numbits == 0:
                temp = self.stream.read(1)
                if len(temp) == 0:
                    self.currentbyte = -1
                    return -1
                self.currentbyte = temp[0]
                self.numbits = 8
            assert self.numbits > 0
            self.numbits -= 1
            return (self.currentbyte >> self.numbits) & 1
        # Write mode - writes a bit to the stream
        else:
            self.currentbyte = (self.currentbyte << 1) | b
            self.numbits += 1
            if self.numbits == 8:
                towrite = bytes((self.currentbyte,))
                self.stream.write(towrite)
                self.currentbyte = 0
                self.numbits = 0




class PpmModel:

    def __init__(self, order, symbollimit, escapesymbol):
        self.model_order = order
        self.symbol_limit = symbollimit
        self.escape_symbol = escapesymbol

        if order >= 0:
            self.root_context = PpmModel.Context(symbollimit, order >= 1)
            self.root_context.frequencies.increment(escapesymbol)
        else:
            self.root_context = None
        self.order_minus1_freqs = frequencies.SimpleFrequencyTable(numsyms=symbollimit, simple_or_flat="Flat")

    def increment_contexts(self, history, symbol):
        if self.model_order == -1:
            return
        if not ((len(history) <= self.model_order) and (0 <= symbol < self.symbol_limit)):
            raise ValueError()

        ctx = self.root_context
        ctx.frequencies.increment(symbol)
        for (i, sym) in enumerate(history):
            subctxs = ctx.subcontexts
            assert subctxs is not None

            if subctxs[sym] is None:
                subctxs[sym] = PpmModel.Context(self.symbol_limit, i + 1 < self.model_order)
                subctxs[sym].frequencies.increment(self.escape_symbol)
            ctx = subctxs[sym]
            ctx.frequencies.increment(symbol)

    # Context - Helper structure
    class Context:

        def __init__(self, symbols, hassubctx):
            self.frequencies = frequencies.SimpleFrequencyTable(freqs=([0] * symbols))
            self.subcontexts = ([None] * symbols) if hassubctx else None
