
def send_receive(comm_chan, data_to_send, timeout):
    byte_data = bytes(data_to_send, 'utf-8')
    comm_chan.send(byte_data)
    return comm_chan.receive(timeout)


def do_command(comm_chan, commandname, parameters, timeout):
    """
        executes a command on the device by sending the string
        commandname(parameters)
    """
    command_string = f"{commandname}({parameters})\r\n"
    result_string = f"{commandname} 00000"
    result = send_receive(comm_chan, command_string, timeout)

    # ToDo: See pg. 30 of reference manual for power source: the last 5
    #      bytes of the response denote an error indication, meaning:
    # 1
    #   0 System is ready to accept a command
    #   1 System is executing a command
    # 2
    #   0 Command is error free
    #   1 Command shows a syntax error or parameter is out of range
    # 3
    #   0 System is ready to execute a command
    #   1 System is running an automatic sequence
    # 4
    #   0 Command execution is error free
    #   1 Command shows an execution error
    # 5
    #   0 Command execution is error free
    #   1 Command shows a time out error

    # check if we've received the answer we were expecting:
    if result_string not in str(result):
        # If we don't receive the correct result string,
        # something is bad. We raise an exception and delegate
        # handling of this error to someone, who knows what to
        # do.
        raise ValueError(f"Result is: \"{str(result)}\"")

    result_value_string = (result[len(result_string) + 1:]).decode('utf-8')      # +1 to skip the first value separating the "xxxxx" from the values
    return result_value_string.strip().split(",")
