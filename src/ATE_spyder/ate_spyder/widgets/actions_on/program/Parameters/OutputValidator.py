class OutputValidator:
    def __init__(self, test_program):
        self.__test_program = test_program
        self.__message = ''
        self.occupied_range = []

    def is_valid_test_number(self, test_num):
        return self.__test_program.is_valid_test_number(test_num)

    def set_invalid_test_number_message(self, test_num: int = None, message: str = None):
        if not test_num or not message:
            self.__message = ''
            return

        self.__message = message

    def get_message(self):
        message = self.__message
        self.__message = ''

        return message
