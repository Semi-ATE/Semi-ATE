from collections import deque


class ResultsCollector:
    def __init__(self, len):
        self._data = deque(maxlen=len)
        self._last_insertion_position = 0

    def append(self, data):
        self._data.append(data)

        if self._last_insertion_position != self._get_size():
            self._last_insertion_position += 1

    def _get_size(self):
        return len(self._data)

    def get_data(self):
        return list(self._data)[:self._last_insertion_position]

    def clear(self):
        self._data.clear()
