import json


class UserSettings:

    @staticmethod
    def get_defaults() -> dict:
        return {
            'master.disabled_site_ids': [],
            'duttest.stop_on_fail': True,
        }

    @staticmethod
    def read_settings_file(path: str) -> dict:
        with open(path) as f:
            json_value = json.load(f)
            if not isinstance(json_value, dict):
                raise ValueError(f'invalid settings file "{path}": content must be a json object, but was "{type(json_value)}"')
            return json_value

    @classmethod
    def write_settings_file(cls, path: str, settings: dict):
        with open(path, 'w') as f:
            json.dump(settings, f, indent=4, sort_keys=True)

    @classmethod
    def load_from_file(cls, path: str) -> dict:
        settings = cls.get_defaults()
        settings_from_file = cls.read_settings_file(path)
        settings.update(settings_from_file)
        return settings

    @classmethod
    def save_to_file(cls, path: str, settings: dict, add_defaults: bool = True):
        settings_to_write = cls.get_defaults() if add_defaults else {}
        settings_to_write.update(settings)
        cls.write_settings_file(path, settings_to_write)
