class SimpleFrequencyTable():

    def __init__(self, freqs=None, numsyms=None, simple_or_flat="Simple"):
        self.simple_or_flat = simple_or_flat
        if self.simple_or_flat == "Flat":
            self.numsymbols = numsyms    # For flat frequency table, just store the number of symbols
        else:
            self.frequencies = list(freqs)
            self.total = sum(self.frequencies)  # Store the total sum of the frequencies
            self.cumulative = None  # Cumulative frequency array

    # Returns the number of symbols in this frequency table
    def get_symbol_limit(self):
        if self.simple_or_flat == "Flat":
            return self.numsymbols
        return len(self.frequencies)     # Simple

    def get(self, symbol):
        if self.simple_or_flat == "Flat":
            return 1
        return self.frequencies[symbol]     # Simple

    # Sets the frequency of the given symbol and updates the total
    def set(self, symbol, freq):
        temp = self.total - self.frequencies[symbol]
        self.total = temp + freq
        self.frequencies[symbol] = freq
        self.cumulative = None

    # Increments the frequency of the given symbol and updates the total
    def increment(self, symbol):
        self.total += 1
        self.frequencies[symbol] += 1
        self.cumulative = None

    # Returns the total of all symbol frequencies
    def get_total(self):
        if self.simple_or_flat == "Flat":
            return self.numsymbols
        return self.total

    # Returns the sum of the frequencies below the given symbol
    def get_low(self, symbol):
        if self.simple_or_flat == "Flat":
            return symbol
        if self.cumulative is None:
            self._init_cumulative()
        return self.cumulative[symbol]

    # Returns the sum of frequencies up to and including the given symbol
    def get_high(self, symbol):
        if self.simple_or_flat == "Flat":
            return symbol + 1
        if self.cumulative is None:
            self._init_cumulative()
        return self.cumulative[symbol + 1]

    # Computes the cumulative frequency array from scratch
    def _init_cumulative(self):
        cumul = [0]
        sum = 0
        for freq in self.frequencies:
            sum += freq
            cumul.append(sum)
        assert sum == self.total
        self.cumulative = cumul



# A wrapper class that validates the arguments and results of the frequency table methods
class FrequenciesTable():

    def __init__(self, freqtab):
        self.freqtable = freqtab

    # Returns the number of symbols in the frequency table
    def get_symbol_limit(self):
        result = self.freqtable.get_symbol_limit()
        return result

    # Returns the frequency of the given symbol
    def get(self, symbol):
        result = self.freqtable.get(symbol)
        return result

    # Returns the total frequency count
    def get_total(self):
        result = self.freqtable.get_total()
        return result

    # Returns the cumulative frequency below the given symbol
    def get_low(self, symbol):
        if self._is_symbol_in_range(symbol):
            low = self.freqtable.get_low(symbol)
            return low
        else:
            self.freqtable.get_low(symbol)

    # Returns the cumulative frequency up to and including the given symbol
    def get_high(self, symbol):
        if self._is_symbol_in_range(symbol):
            low = self.freqtable.get_low(symbol)
            high = self.freqtable.get_high(symbol)
            return high
        else:
            self.freqtable.get_high(symbol)

    # Sets the frequency of the given symbol
    def set(self, symbol, freq):
        self.freqtable.set(symbol, freq)

    # Increments the frequency of the given symbol
    def increment(self, symbol):
        self.freqtable.increment(symbol)

    # Checks if the symbol is within the valid range
    def _is_symbol_in_range(self, symbol):
        return 0 <= symbol < self.get_symbol_limit()
