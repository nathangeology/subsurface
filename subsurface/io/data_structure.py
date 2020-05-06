from abc import ABC
import pandas as pd


class DataStructure(ABC):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.subtable_index = pd.DataFrame()

    def get_data(self, *, key):
        try:
            data_table_info = self.subtable_index.loc[key]
        except Exception as ex:
            print('data not found')
            return pd.DataFrame()
        # TODO: Get table from cache
        raise(NotImplementedError('Not Done!'))

    def set_data(self, *, data, key):
        if key in self.subtable_index.index:
            print('load data to replace/append/update')
        else:
            # TODO: Write data to cache
            pass
        raise(NotImplementedError('Not Done!'))

    def remove_data(self, *, key):
        raise(NotImplementedError('Not Done!'))

    def key_exists(self, key):
        raise (NotImplementedError('Not Done!'))
