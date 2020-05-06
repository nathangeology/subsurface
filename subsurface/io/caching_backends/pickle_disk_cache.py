import pickle
from ..abstractcache import AbstractCache
# from crcdal.input_layer.configuration import Configuration
from crcdal.input_layer.configuration_singleton import Configuration

from ..utilities.exception_handling import function_raises_val
import pkg_resources
import os
from crcdal.data_layer.utilities.exception_tracking import ExceptionTracking
from crcdal.output_layer.utilities.progress_monitor import \
            ProgressMonitor
import sys


class PickleDiskCache(AbstractCache):
    def __init__(self):
        super().__init__()

    def read_from_cache(self, name):
        if self.check_cache(name):
            path = self.get_path(name)
            return self.read_pickle(path)
        else:
            return None

    def write_to_cache(self, name, data_structure):
        path = self.get_path(name)
        self.write_pickle(path, data_structure)

    def delete_from_cache(self, name):
        if self.check_cache(name):
            file_path = self.make_path_a_filename(self.get_path(name))
            try:
                os.remove(file_path)
            except Exception as ex:
                print('delete failed')
                print(ex)

    def check_cache(self, name):
        path = self.get_path(name)
        return pkg_resources.resource_exists('crcdal', path)

    @staticmethod
    def get_path(name):
        subfolder = Configuration().get_cache_subfolder()
        cache_path = 'cache/' + subfolder + '/' + name + '.pkl'
        return cache_path

    @function_raises_val(None, 'Reading Pickle Failed', 'Cache Fail')
    def read_pickle(self, path):
        objects = []
        path = self.make_path_a_filename(path)
        with (open(path, "rb")) as openfile:
            while True:
                try:
                    objects.append(pickle.load(openfile))
                except EOFError:
                    break
            output = objects[0]
        return output

    @function_raises_val(None, 'Writing Pickle Failed', 'Cache Fail')
    def write_pickle(self, path, obj):
        pkg_resources.ensure_directory(path)
        file_path = self.make_path_a_filename(path)
        with open(file_path, "wb") as f:
            try:
             pickle.dump(obj, f)
            except MemoryError:
                ExceptionTracking().log_exception('ran out of memory',
                                                  'wellgroup',
                                                  self.identifier_name)
                memsize = sys.getsizeof(self)
                ProgressMonitor().quick_report(
                    'Critical Memory Error object too big. size of object: {}'
                        .format(memsize))

    def make_path_a_filename(self, path):
        path = pkg_resources.resource_filename('crcdal', path)
        return path
