from handlerApp.handler_application import HandlerApplication
from ATE.apps.common.configuration_reader import ConfigReader


if __name__ == "__main__":
    config = ConfigReader("./handler_config_file.json")
    configuration = config.get_configuration()

    app = HandlerApplication(configuration)
    app.run()
