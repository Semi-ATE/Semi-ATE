from ATE.TCC.Actuators.MagfieldSTL.driver.commandbuilder import CommandBuilder
from ATE.TCC.Actuators.MagfieldSTL.driver.util import send_receive, do_command


class DCS6K:
    """
    This class contains the refernce implementation for the
    STL Dgital Current Source DCS-6K 

    For details on the behavior of each function refer to the
    reference manual of the device.

    The C'tor expects an instance of a communications channel.
    """
    def __init__(self, comm_chan):
        self.comm_chan = comm_chan
        self.command_builder = CommandBuilder(comm_chan)
        pass

    def is_connected(self):
        return self.comm_chan.is_connected()

    def __send_receive(self, data_to_send, timeout):
        return send_receive(self.comm_chan, f"{data_to_send}\r\n", timeout)

    def __do_command(self, commandname, parameters, timeout):
        results = do_command(self.comm_chan, commandname, parameters, timeout)
        result_dict = {}
        for index, result_value in enumerate(results):
            result_dict[f"value{index}"] = result_value
        result_dict["status"] = "ok"
        return result_dict

    def query_id(self):
        result = self.__send_receive("*IDN?", 2500).decode("utf-8")
        if "STL DCS-6K" not in result:
            raise IOError("Bad stl type.")
        return result[11:]

    def clear_sequences(self):
        return self.__do_command("ClearSequences", "", 7000)

    def initialize_pid(self):
        return self.__do_command("InitializePID", "", 2000)

    def make_init_pid_2(self, pid_type):
        return self.command_builder.init_command("InitializePID") \
                   .constrain_value_parameter("pid-type", ["standard", "fast", "slow", "ext", "all"], pid_type) \
                   .with_timeout(2000)

    def initialize_pid_2(self, pid_type, dry):
        return self.make_init_pid_2(pid_type).execute(dry)

    def measure_current_impedance(self):
        return self.__do_command("MeasureCurrentImpedance", "", 10000)

    def perform_impedance_test(self):
        return self.__do_command("PerformImpedanceTest", "", 10000)

    def perform_selftest(self):
        return self.__do_command("PerformSelfTest", "", 5000)

    def read_analog_parameters(self):
        return self.__do_command("ReadAnalogParameters", "", 1500)

    def read_analog_voltage_to_field(self):
        return self.__do_command("ReadAnalogVoltageToField", "", 1500)

    def read_current(self):
        return self.__do_command("ReadCurrent", "", 1500)

    def read_current_sequence_line(self):
        return self.__do_command("ReadCurrentSequenceLine", "", 1500)

    def read_ethernet_config(self):
        return self.__do_command("ReadEthernetConfig", "", 1500)

    def read_feedback_mode(self):
        return self.__do_command("ReadFeedbackMode", "", 1500)

    def read_field_to_current(self):
        return self.__do_command("ReadFieldToCurrent", "", 1500)

    def make_read_free_memory(self, address):
        return self.command_builder.init_command("ReadFreeMemory") \
                   .constrain_numeric_parameter("address", 0, 65536, address) \
                   .with_timeout(1500)

    def read_free_memory(self, address, dry):
        return self.make_read_free_memory(address).execute(dry)

    def read_hardware_state(self):
        return self.__do_command("ReadHardwareState", "", 1500)

    def read_hardware_version(self):
        return self.__do_command("ReadHardwareVersion", "", 1500)

    def read_max_current(self):
        return self.__do_command("ReadMaxCurrent", "", 1500)

    def read_max_voltage(self):
        return self.__do_command("ReadMaxVoltage", "", 1500)

    def read_operation_mode(self):
        return self.__do_command("ReadOperationMode", "", 1500)

    def read_output_state(self):
        return self.__do_command("ReadOutputState", "", 1500)

    def make_read_pid(self, pid_type):
        return self.command_builder.init_command("ReadPID") \
                   .constrain_value_parameter("pid_type", ["standard", "fast", "smooth", "ext"], pid_type) \
                   .with_timeout(1500)

    def read_pid(self, pid_type, dry):
        return self.make_read_pid(pid_type).execute(dry)

    def read_reference_impedance(self):
        return self.__do_command("ReadReferenceImpedance", "", 1500)

    def read_reference_sensor_parameters(self):
        return self.__do_command("ReadReferenceSensorParameters", "", 1500)

    def make_read_read_sequence_line(self, address):
        return self.command_builder.init_command("ReadSequenceLine") \
                   .constrain_numeric_parameter("address", 0, 65536, address) \
                   .with_timeout(1500)

    def read_sequence_line(self, address, dry):
        return self.make_read_read_sequence_line(address).execute(dry)

    def read_serial_number(self):
        return self.__do_command("ReadSerialNumber", "", 1500)

    def read_startup_mode(self):
        return self.__do_command("ReadStartupMode", "", 1500)

    def read_status(self):
        return self.__do_command("ReadStatus", "", 1500)

    def read_timer(self):
        return self.__do_command("ReadTimer", "", 1500)

    def read_trigger(self):
        return self.__do_command("ReadTrigger", "", 1500)

    def make_read_user_value(self, contr):
        return self.command_builder.init_command("ReadUserValue") \
                   .constrain_value_parameter("contr", ["intern", "extern"], contr) \
                   .with_timeout(1500)

    def read_user_value(self, contr, dry):
        return self.make_read_user_value(contr).execute(dry)

    def read_value(self):
        return self.__do_command("ReadValue", "", 1500)

    def read_voltage(self):
        return self.__do_command("ReadVoltage", "", 1500)

    def restore_factory_defaults(self):
        return self.__do_command("RestoreFactoryDefaults", "", 12000)

    def make_set_analog_parameters(self, tolerance, pid_type, trigger, toltime):
        return self.command_builder.init_command("SetAnalogParameters") \
                   .constrain_numeric_parameter("tolerance", 0, 2000, tolerance) \
                   .constrain_value_parameter("pid_type", ["standard", "fast", "smooth", "ext"], pid_type) \
                   .constrain_value_parameter("trigger", [0, 1], trigger) \
                   .constrain_numeric_parameter("toltime", 0, 1000, toltime) \
                   .with_timeout(1500)

    def set_analog_parameters(self, tolerance, pid_type, trigger, toltime, dry):
        return self.make_set_analog_parameters(tolerance, pid_type, trigger, toltime).execute(dry)

    def make_set_analog_voltage_to_field(self, slope, offset):
        return self.command_builder.init_command("SetAnalogParameters") \
                   .constrain_numeric_parameter("slope", -125, 125, slope) \
                   .constrain_numeric_parameter("offset", -2000, 2000, slope) \
                   .with_timeout(1500)

    def set_analog_voltage_to_field(self, slope, offset, dry):
        return self.make_set_analog_voltage_to_field().execute(dry)

    def set_ethernet_config(self, ip, submask, gateway, port):
        return self.__do_command("ReadOutputState", f"{ip},{submask},{gateway},{port}", 1500)

    def make_set_feedback_mode(self, mode):
        return self.command_builder.init_command("SetFeedbackMode") \
                   .constrain_value_parameter("mode", ["norm", "none"], mode) \
                   .with_timeout(1500)

    def set_feedback_mode(self, mode, dry):
        return self.make_set_feedback_mode(mode).execute(dry)

    def make_set_free_memory(self, address, value):
        return self.command_builder.init_command("ReadFreeMemory") \
                   .constrain_numeric_parameter("address", 0, 32768, address) \
                   .constrain_numeric_parameter("value"), 0, 255 \
                   .with_timeout(1500)

    def set_free_memory(self, address, value, dry):
        return self.make_set_free_memory(address, value).execute(dry)

    def make_set_field_to_current(self, slope, offset):
        return self.command_builder.init_command("SetFieldToCurrent") \
                   .constrain_numeric_parameter("slope", -125, 125, slope) \
                   .constrain_numeric_parameter("offset", -2000, 2000, slope) \
                   .with_timeout(1500)

    def set_field_to_current(self, slope, offset, dry):
        return self.make_set_field_to_current(slope, offset).execute(dry)

    def make_set_max_current(self, max_i):
        return self.command_builder.init_command("SetMaxCurrent") \
                   .constrain_numeric_parameter("maxI", 0.1, 10, max_i) \
                   .with_timeout(1500)

    def set_max_current(self, max_i, dry):
        return self.make_set_max_current(max_i).execute(dry)

    def make_set_max_voltage(self, max_v):
        return self.command_builder.init_command("SetMaxVoltage") \
                   .constrain_numeric_parameter("maxV", 0.1, 200, max_v) \
                   .with_timeout(1500)

    def set_max_voltage(self, max_v, dry):
        return self.make_set_max_voltage(max_v).execute(dry)

    def make_set_operation_mode(self, mode):
        return self.command_builder.init_command("SetOperationMode") \
                   .constrain_value_parameter("mode", ["analog", "digital"], mode) \
                   .with_timeout(1500)

    def set_operation_mode(self, mode, dry):
        return self.make_set_operation_mode(mode).execute(dry)

    def make_set_output_state(self, mode):
        return self.command_builder.init_command("SetOutputState") \
                   .constrain_value_parameter("mode", ["active", "off"], mode) \
                   .with_timeout(1500)

    def set_output_state(self, mode, dry):
        return self.make_set_output_state(mode).execute(dry)

    def make_set_pid(self, pid_type, proportional_factor, integral_factor, slew_rate):
        return self.command_builder.init_command("SetPID") \
                   .constrain_value_parameter("pid_type", ["standard", "fast", "smooth", "ext"], pid_type) \
                   .constrain_numeric_parameter("proportional_factor", 0, 800, proportional_factor) \
                   .constrain_numeric_parameter("integral_factor", 0, 4e6, integral_factor) \
                   .constrain_numeric_parameter("slew_rate", 0, 5e5, slew_rate) \
                   .with_timeout(1500)

    def set_pid(self, pid_type, proportional_factor, integral_factor, slew_rate, dry):
        return self.make_set_pid(pid_type, proportional_factor, integral_factor, slew_rate).execute(dry)

    def make_set_reference_impedance(self, res_load_ref, ind_load_ref, max_res_load_dev, max_ind_load_dev):
        return self.command_builder.init_command("SetReferenceImpedance") \
                   .constrain_numeric_parameter("res_load_ref", 0, 1000, res_load_ref) \
                   .constrain_numeric_parameter("ind_load_ref", 0, 1000, ind_load_ref) \
                   .constrain_numeric_parameter("max_res_load_dev", 0, 1000, max_res_load_dev) \
                   .constrain_numeric_parameter("max_ind_load_dev", 0, 1000, max_ind_load_dev) \
                   .with_timeout(1500)

    def set_reference_impedance(self, res_load_ref, ind_load_ref, max_res_load_dev, max_ind_load_dev, dry):
        return self.make_set_reference_impedance(res_load_ref, ind_load_ref, max_res_load_dev, max_ind_load_dev).execute(dry)

    def make_set_reference_impedance_2(self, res_load_ref, ind_load_ref):
        return self.command_builder.init_command("SetReferenceImpedance") \
                   .constrain_numeric_parameter("res_load_ref", 0, 1000, res_load_ref) \
                   .constrain_numeric_parameter("ind_load_ref", 0, 1000, ind_load_ref) \
                   .with_timeout(1500)

    def set_reference_impdance_2(self, res_load_ref, ind_load_ref, dry):
        return self.make_set_reference_impedance_2(res_load_ref, ind_load_ref).execute(dry)

    def make_set_reference_sensor_parameters(self, sensivity, offset):
        return self.command_builder.init_command("SetReferenceSensorParameters") \
                   .constrain_numeric_parameter("sens", -125, 125, sensivity) \
                   .constrain_numeric_parameter("offset", -2000, 2000, offset) \
                   .with_timeout(1500)

    def set_reference_sensor_parameters(self, sensivity, offset, dry):
        return self.make_set_reference_sensor_parameters(sensivity, offset).execute(dry)

    def make_set_sequence_line(self, address, amp, tolerance, toltime, pid_type, maker_output):
        return self.command_builder.init_command("SetSequenceLine") \
                   .constrain_numeric_parameter("address", 1, 65536, address) \
                   .constrain_numeric_parameter("amp", -20000, 2000, amp) \
                   .constrain_numeric_parameter("tolerance", 0, 2000, tolerance) \
                   .constrain_numeric_parameter("toltime", 0, 1000, toltime) \
                   .constrain_value_parameter("pid_type", ["standard", "fast", "smooth", "ext"], pid_type) \
                   .constrain_value_parameter("marker", [0, 1], maker_output) \
                   .with_timeout(1500)

    def set_sequence_line(self, address, amp, tolerance, toltime, pid_type, maker_output, dry):
        return self.make_set_sequence_line(address, amp, tolerance, toltime, pid_type, maker_output).execute(dry)

    def make_set_startup_mode(self, mode):
        return self.command_builder.init_command("SetStartupMode") \
                   .constrain_value_parameter("mode", ["analog", "digital"], mode) \
                   .with_timeout(1500)

    def set_startup_mode(self, mode, dry):
        return self.make_set_startup_mode(mode).execute(dry)

    def make_set_value(self, value):
        return self.command_builder.init_command("SetValue") \
                   .constrain_numeric_parameter("value", -2000, 2000, value) \
                   .with_timeout(1500)

    def set_value(self, value, dry):
        return self.make_set_value(value).execute(dry)

    def make_set_user_value(self, value):
        return self.command_builder.init_command("SetUserValue") \
                   .constrain_numeric_parameter("value", -2000, 2000, value) \
                   .with_timeout(1500)

    def set_user_value(self, value, dry):
        # Note: RefMan lists slewrate, type and contr as additional parameters
        # but TDK reference implementation uses internal defaul values of the
        # source here by not sending the values
        return self.make_set_value(value).execute(dry)

    def make_start_sequence(self, start, stop, rep, proc, runtime, contr, timeout):
        return self.command_builder.init_command("StartSequence") \
                   .constrain_numeric_parameter("start", 1, 65536, start) \
                   .constrain_numeric_parameter("stop", 1, 65536, stop) \
                   .constrain_numeric_parameter("rep", 1, 1024, rep) \
                   .constrain_value_parameter("proc", ["trigger", "time"], proc) \
                   .constrain_numeric_parameter("runtime", 0.0001, 10000, runtime) \
                   .constrain_value_parameter("contr", ["intern", "extern"], contr) \
                   .constrain_numeric_parameter("time-out", 0.0001, 10000, timeout) \
                   .with_timeout(1500)

    def start_sequence(self, start, stop, rep, proc, runtime, contr, timeout, dry):
        return self.make_start_sequence(start, stop, rep, proc, runtime, contr, timeout).execute(dry)

    def stop_sequence(self):
        return self.__do_command("StopSequence", "", 1500)
