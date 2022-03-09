from typing import Callable
import os
import json

from ate_projectdatabase.Types import Types

CONFIG_DIR_NAME = 'definitions'


class DBObject:
    def to_dict(self) -> dict:
        return self.__dict__

    def write_attribute(self, member_name: str, value):
        self.__dict__[member_name] = value

    def read_attribute(self, attribute_name: str):       # Returntype can be just about anything!
        return self.__dict__[attribute_name]

    def has_attribute(self, attribute_name: str) -> bool:
        return attribute_name in self.__dict__


class FileOperator:
    def __init__(self, project_dir: str):
        self.config_dir = os.path.join(project_dir, CONFIG_DIR_NAME)
        self.data_cache = {}
        self.query_open = False
        self.filter_expression = lambda x: True
        self.sort_expression = None
        self.current_type = None
        self.current_subtypes = []

    @staticmethod
    def _make_db_object(json_dict: dict) -> DBObject:
        current_object = DBObject()
        for k, v in json_dict.items():
            setattr(current_object, k, v)
        return current_object

    def get_current_target_list_name(self) -> str:
        '''
            Tricky: A query can concern multiple files, however,
            if we want to add an item it shall only ever be added
            to a single file. To find out, which file that is, we
            build the path pattern and take the first file, that
            matches, throwing an exception if more than one file
            matches and generating a new filename if no name file
            matches
        '''
        file_path = self.generate_path(self.current_type, self.current_subtypes)
        import glob
        if len(glob.glob(file_path)) > 1:
            raise IOError("Tried to add data to multiple files")
        if len(glob.glob(file_path)) == 1:
            return glob.glob(file_path).pop(0)

        # Generate new filename, as apparently no file exists...
        the_type = self.generate_path_base(self.current_type, self.current_subtypes)
        file_path = os.path.join(self.config_dir, self.current_type, f'{the_type}.json')
        self.data_cache[file_path] = []
        return file_path

    def load_configuration(self, type: Types, subtypes: list):
        file_path = self.generate_path(type, subtypes)
        self.data_cache = {}

        import glob
        for f in glob.glob(file_path):
            try:
                with open(f, 'r') as f:
                    loaded_data = json.load(f)
                    return_val = []
                    for item in loaded_data:
                        return_val.append(self._make_db_object(item))
                self.data_cache[f.name] = return_val
            except Exception:
                self.data_cache[f.name] = []

        # nastyness: if nothing was found in the FS we atleast create
        # the file thet specifies our filename:
        if len(self.data_cache) == 0:
            file_path = file_path.replace("*", "")
            self.data_cache[file_path] = []

    def store_configuration(self):
        # DBObjects are not easily serializable, we serialize
        # them each on their own...
        for name, itemlist in self.data_cache.items():
            print(f'Name: {name}')
            data_to_write = []
            for item in itemlist:
                data_to_write.append(item.__dict__)

            if len(data_to_write) > 0:
                with open(name, 'w') as f:
                    json.dump(data_to_write, f, indent=2)
            else:
                # delete file if still there,
                # but no records are available for the file.
                if os.path.exists(name):
                    os.remove(name)

    def generate_path_base(self, type: Types, subtypes: list) -> str:
        the_type = type
        for subtype in subtypes:
            the_type = the_type + subtype
        return the_type

    def generate_path(self, type: Types, subtypes: list) -> str:
        self.current_type = type
        self.current_subtypes = subtypes

        the_type = self.generate_path_base(type, subtypes)

        file_path = os.path.join(self.config_dir, type, f'{the_type}*.json')
        return file_path

    def query(self, type: Types):
        # self.data_cache contains the complete representation of the available data and is
        # always current provided no two instances of the FileOperator work on the
        # same dataset. This means we can avoid hitting masstorage for loading if
        # the dataset (i.e. type!) did not change between two consecutive calls
        # to query.
        self.query_with_subtype(type, [])
        return self

    def query_with_subtype(self, type: Types, subtypes: list):
        if type != self.current_type or subtypes != self.current_subtypes:
            self.load_configuration(type, subtypes)
            self.current_type = type
            self.current_subtypes = subtypes
        self.query_open = True
        self.filter_expression = lambda x: True
        self.sort_expression = None
        return self

    def filter(self, filter_expression: Callable):
        if self.query_open is False:
            raise Exception("Cannot apply filter when no query is open.")
        self.filter_expression = filter_expression
        return self

    def sort(self, sort_expression: Callable):
        if self.query_open is False:
            raise Exception("Cannot sort when no query is open.")
        self.sort_expression = sort_expression
        return self

    def all(self) -> list:
        if self.query_open is False:
            raise Exception("Cannot get 'all' when no query is open.")
        data = list(x for x in self._items() if self.filter_expression(x))
        if self.sort_expression is not None:
            data = sorted(data, key=self.sort_expression)
        return data

    def one(self) -> DBObject:
        if self.query_open is False:
            raise Exception("Cannot get 'one' when no query is open.")
        items = self.all()
        assert (len(items) == 1)
        return items[0]

    def one_or_none(self) -> DBObject:
        if self.query_open is False:
            raise Exception("Cannot get 'one or none' when no query is open.")
        items = self.all()
        if len(items) == 0:
            return None
        # If we have items, having more than one is an error in this case!
        assert (len(items) == 1)
        return items[0]

    def _items(self):
        import itertools
        all_loaded_items = [y for _, y in self.data_cache.items()]
        all_loaded_items = [x for x in itertools.chain(*all_loaded_items)]
        return all_loaded_items

    def delete(self):
        if self.query_open is False:
            raise Exception("Cannot 'delete' when no query is open.")
        for f, items in self.data_cache.items():
            new_list = list(x for x in items if self.filter_expression(x) is False)
            self.data_cache[f] = new_list
        return self

    def delete_item(self, item: DBObject):
        if self.query_open is False:
            raise Exception("Cannot 'delete_item' when no query is open.")
        self.data_cache.pop(item)
        return self

    def insert(self, objects: list):
        if self.query_open is False:
            raise Exception("Cannot 'insert'' when no query is open.")
        for item in objects:
            for f, itemlist in self.data_cache.items():
                itemlist.append(self._make_db_object(item))
        return self

    def add(self, object: dict):
        if self.query_open is False:
            raise Exception("Cannot 'insert' when no query is open.")
        list_name = self.get_current_target_list_name()
        self.data_cache[list_name].append(self._make_db_object(object))
        return self

    def count(self) -> int:
        if self.query_open is False:
            raise Exception("Cannot 'count' when no query is open.")
        return len(self.all())

    def commit(self):
        if self.query_open is False:
            raise Exception("Cannot 'commit' when no query is open.")
        self.store_configuration()
        self.query_open = False

    def rename(self, type: Types, old_name: str, new_name: str):
        base_path = os.path.join(self.config_dir, self.generate_path_base(type, []))
        old_name = f"{type}{old_name}.json"
        new_name = f"{type}{new_name}.json"
        old_path = os.path.join(base_path, old_name)
        new_path = os.path.join(base_path, new_name)
        os.rename(old_path, new_path)
