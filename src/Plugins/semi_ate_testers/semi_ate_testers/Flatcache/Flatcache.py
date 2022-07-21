import requests
import json
from pydantic import BaseModel


class FlatcacheConfig(BaseModel):
    ip: str
    port: int


class Flatcache:
    def __init__(self):
        self.config: FlatcacheConfig = None
        self.target_ip = ""
        self.target_port = ""
        self.last_part_id = ""
        self.fetched_data = {}
        self.subdoc_cache = {}

    def apply_configuration(self, data: dict):
        self.config = FlatcacheConfig(**data)

        # Canary request -> check if service is available (i.e. requests succeeds)
        # and if it reports the correct API version.
        r = requests.get(self.url('api'))
        api_version = json.loads(r.content)
        version = api_version["version"]
        if version != 1:
            raise ValueError(f"Expected flatcache api version to be 1, but is {version}")

    def get_value(self, part_id: str, value_name: str) -> dict:
        if self.last_part_id != part_id:
            self.do_fetch(part_id)

        # The valuename is composed of <programname>.<testinstancename>.<paramname>
        # the programname is used as catflache subdoc id, so we split that off to
        # get the right subdoc:
        value_parts = value_name.split(".", 1)
        subdocid = value_parts[0]
        normalized_value_name = value_parts[1]

        found_subdoc = self.fetched_data.get(subdocid)

        if found_subdoc is None:
            return None

        for record in found_subdoc:
            record_type = record["type"]
            if record_type == "PTR":
                if record["TEST_TXT"] == normalized_value_name:
                    return record

            if record_type == "PIR" and value_name == "PIR":
                return record

            if record_type == "PRR" and value_name == "PRR":
                return record

    def get_cached_value(self, value_name: str) -> dict:
        return self.get_value(self.last_part_id, value_name)

    def do_fetch(self, part_id):
        r = requests.get(self.url(part_id))
        try:
            values = json.loads(r.content)
            self.last_part_id = part_id
            self.fetched_data = {}
            for entry in values["contents"]:
                fetched_data = json.loads(entry["contents"])
                subdoc_id = entry["subdocid"]
                self.fetched_data[subdoc_id] = fetched_data

        except Exception as e:
            print(e)
            print(r.content)

    def publish(self, part_id: str, program_name: str, data):
        # Trouble: This will completely replace the date stored in the cache
        #  with "data" -> we don't want that.
        requests.put(self.url(part_id), json={"subdocid": str(program_name), "contents": json.dumps(data)})

    def drop_part(self, part_id: str):
        requests.delete(self.url(part_id))

    def utl(self, part_id: str):
        return f"http://{self.config.ip}:{self.config.port}/{part_id}"

