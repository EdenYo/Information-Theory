import frequencies



class ArithmeticCoderBase:

    def __init__(self, numbits):
        self.num_state_bits = numbits  # Store the number of bits used for the state
        self.full_range = 1 << self.num_state_bits  # Calculate the full range of possible states (2^numbits)
        self.half_range = self.full_range >> 1  # Calculate half the range, ensuring it is non-zero
        self.quarter_range = self.half_range >> 1  # Calculate quarter range, which can potentially be zero
        self.min_range = self.quarter_range + 2  # Minimum range should allow at least 2 states
        self.max_range = self.min_range  # Initialize maximum total range, starting from minimum range
        self.state_mask = self.full_range - 1  # Create a mask to limit the state values to the defined range

        self.low = 0
        self.high = self.state_mask

    def update(self, freqs, symbol):
        range = self.high - self.low + 1  # Calculate the current range based on low and high values
        total = freqs.get_total()  # Retrieve total frequencies and frequencies for the specified symbol
        symlow = freqs.get_low(symbol)
        symhigh = freqs.get_high(symbol)

        # Update the low and high values based on the symbol's frequencies
        updated_low = self.low + symlow * range // total
        updated_high = self.low + symhigh * range // total - 1
        self.low = updated_low
        self.high = updated_high

        # Shift out bits while low and high have the same top bit value
        while ((self.low ^ self.high) & self.half_range) == 0:
            self.shift(False)
            self.low = ((self.low << 1) & self.state_mask)  # Update low value
            self.high = ((self.high << 1) & self.state_mask) | 1  # Update low value

        # Delete the second highest bit of both while low's top two bits are 01 and high's are 10
        while (self.low & ~self.high & self.quarter_range) != 0:
            self.underflow()  # Handle underflow condition
            self.low = (self.low << 1) ^ self.half_range  # Update low value
            self.high = ((self.high ^ self.half_range) << 1) | self.half_range | 1  # Update high value

    # Handle the case when 'low' and 'high' share the same top bit.
    def shift(self, is_compute=True):
        if is_compute is False:
            return

    # Called to manage the scenario when 'low' has the form 01(...) and 'high' has the form 10(...).
    def underflow(self, is_compute=True):
        if is_compute is False:
            return


class ArithmeticEncoder(ArithmeticCoderBase):

    def __init__(self, numbits, bitout):
        super(ArithmeticEncoder, self).__init__(numbits)
        self.num_underflow = 0
        self.output = bitout

    # Encodes the given symbol using the provided frequency table, updating the coder's state and writing out bits as necessary.
    def write(self, freqs, symbol):
        if not isinstance(freqs, frequencies.FrequenciesTable):
            freqs = frequencies.FrequenciesTable(freqs)
        self.update(freqs, symbol)

    # Shifts the current state of the encoder by writing out the most significant bit of 'low' to the output.
    # Handles potential underflow by writing opposite bits when necessary.
    def shift(self, is_compute=True):
        bit = self.low >> (self.num_state_bits - 1)  # Extract the most significant bit from 'low'
        self.output.handle_file(bit)

        for _ in range(self.num_underflow):
            self.output.handle_file(bit ^ 1)
        self.num_underflow = 0

    def underflow(self, is_compute=True):
        self.num_underflow += 1  # Increment the count of underflow occurrences.

    # Completes the arithmetic coding process by flushing any buffered bits to ensure accurate decoding,
    # while keeping the output stream open.
    def finish(self):
        self.output.handle_file(1)


class ArithmeticDecoder(ArithmeticCoderBase):

    def __init__(self, numbits, bitin):
        super(ArithmeticDecoder, self).__init__(numbits)
        self.input = bitin  # Initialize the underlying bit input stream.
        self.code = 0  # Initialize the buffered raw code bits, which will always fall within the range [low, high].
        for _ in range(self.num_state_bits):
            self.code = self.code << 1 | self.read_code_bit()

    # Decodes the next symbol using the provided frequency table and returns the result.
    # Additionally, updates the internal state of the arithmetic decoder and may consume more input bits.
    def read(self, freqs):
        if not isinstance(freqs, frequencies.FrequenciesTable):
            freqs = frequencies.FrequenciesTable(freqs)

        # Retrieve the total frequency count from the table
        total = freqs.get_total()

        current_range = self.high - self.low + 1
        offset = self.code - self.low
        value = ((offset + 1) * total - 1) // current_range

        # Perform a binary search to find the symbol whose cumulative frequency is closest to 'value'
        start = 0
        end = freqs.get_symbol_limit()
        while end - start > 1:
            middle = (start + end) >> 1  # Narrow the search range based on the current middle point
            if freqs.get_low(middle) > value:
                end = middle
            else:
                start = middle

        self.update(freqs, start)
        return start  # Return the decoded symbol.

    def shift(self, is_compute=True):
        self.code = ((self.code << 1) & self.state_mask) | self.read_code_bit()

    def underflow(self, is_compute=True):
        self.code = (self.code & self.half_range) | ((self.code << 1) & (self.state_mask >> 1)) | self.read_code_bit()

    # Retrieves the next bit (0 or 1) from the input stream. If the stream ends,
    # it is assumed to produce an infinite sequence of trailing zeros.
    def read_code_bit(self):
        temp = self.input.handle_file()
        if temp == -1:
            temp = 0
        return temp