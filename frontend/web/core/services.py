class SummaryListHelper:

    def __init__(self):
        self._summary_list_id_counter = -1

    @property
    def summary_list_id_counter(self):
        self._summary_list_id_counter += 1
        return self._summary_list_id_counter

    @staticmethod
    def make_row(key, value, url):
        return {
            'key': key,
            'value': value,
            'action': {
                'url': url
            }
        }

    def make_summary_list(self, heading, rows):
        return {
            'id': f'id_summary_list_{self.summary_list_id_counter}',
            'heading': heading,
            'rows': rows
        }
