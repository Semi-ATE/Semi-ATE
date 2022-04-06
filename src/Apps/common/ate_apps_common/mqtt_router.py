import re

class MqttRouter:
    def __init__(self):
        self.routes = {}

    def register_route(self, topic_regex: str, callback: callable):
        if topic_regex not in self.routes:
            self.routes[topic_regex] = []
        self.routes[topic_regex].append(callback)

    def unregister_route(self, topic_regex: str):
        if topic_regex not in self.routes:
            return
        self.routes.pop(topic_regex)

    def inject_message(self, topic, message):
        for route in self.routes:
            result = re.search(route, topic)
            if result is not None:
                for callback in self.routes[route]:
                    callback(topic, message)
