import paho.mqtt.client as mqtt
import sparkplug_b_pb2 as spb
from st14 import St14Data

import sys
import ssl
import certifi

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from qt.sparkplug_demo import Ui_MainWindow

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
	bus_voltage_received = pyqtSignal(float)
	battery_voltage_received = pyqtSignal(float)
	current_received = pyqtSignal(float)
	min_cell_voltage_received = pyqtSignal(float)
	max_cell_voltage_received = pyqtSignal(float)
	min_cell_temp_received = pyqtSignal(float)
	max_cell_temp_received = pyqtSignal(float)
	inlet_temp_received = pyqtSignal(float)
	outlet_temp_received = pyqtSignal(float)
	op_status_received = pyqtSignal(int)
	bus_status_received = pyqtSignal(int)
	hvil_status_received = pyqtSignal(int)
	soc_received = pyqtSignal(float)
	charge_power_received = pyqtSignal(float)
	discharge_power_received = pyqtSignal(float)

	def __init__(self):
		super().__init__()

		self.bus_voltage_received.connect(self.update_bus_voltage_field)
		self.battery_voltage_received.connect(self.update_battery_voltage_field)
		self.current_received.connect(self.update_current_field)
		self.min_cell_voltage_received.connect(self.update_min_cell_voltage_field)
		self.max_cell_voltage_received.connect(self.update_max_cell_voltage_field)
		self.min_cell_temp_received.connect(self.update_min_cell_temp_field)
		self.max_cell_temp_received.connect(self.update_max_cell_temp_field)
		self.inlet_temp_received.connect(self.update_inlet_temp_field)
		self.outlet_temp_received.connect(self.update_outlet_temp_field)
		self.op_status_received.connect(self.update_op_status_field)
		self.bus_status_received.connect(self.update_bus_status_field)
		self.hvil_status_received.connect(self.update_hvil_status_field)
		self.soc_received.connect(self.update_soc_field)
		self.charge_power_received.connect(self.update_charge_power_field)
		self.discharge_power_received.connect(self.update_discharge_power_field)
		
		self.init_mqtt()  # Set up the UI from Designer
		self.setupUi(self)  # Set up the UI from Designer

	def init_mqtt(self):
		# Create an MQTT client instance
		self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.st14 = St14Data()
		self.client.tls_set(ca_certs=certifi.where(), cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
		self.client.connect("broker.hivemq.com", 8883, 60)
		self.client.loop_start()

	# The callback for when the client receives a CONNACK response from the server
	def on_connect(self, client, userdata, flags, reason_code, properties):
		print("Connected with result code "+str(reason_code))
		client.subscribe("spBv1.0/spb_docker_test_app/DDATA/st14/#")
		client.subscribe("spBv1.0/spb_docker_test_app/DBIRTH/st14/#")

	# The callback for when a PUBLISH message is received from the server
	def on_message(self, client, userdata, msg):
		try:
			payload = spb.Payload()
			payload.ParseFromString(msg.payload)
			for metric in payload.metrics:
				match metric.datatype:
					case 5:
						self.st14.data[metric.name] = metric.int_value
					case 9:
						self.st14.data[metric.name] = metric.float_value
				
				match metric.name:
					case "HVES1_Bus_Voltage":
						self.bus_voltage_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Voltage_Level":
						self.battery_voltage_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Current":
						self.current_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Lowest_Cell_Voltage":
						self.min_cell_voltage_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Highest_Cell_Voltage":
						self.max_cell_voltage_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Lowest_Cell_Temperature":
						self.min_cell_temp_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Highest_Cell_Temperature":
						self.max_cell_temp_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Intake_Coolant_Temperature":
						self.inlet_temp_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Outlet_Coolant_Temperature":
						self.outlet_temp_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Operational_Status":
						self.op_status_received.emit(int(self.st14.data[metric.name]))
					case "HVES1_High_Voltage_Bus_Connection_Status":
						self.bus_status_received.emit(int(self.st14.data[metric.name]))
					case "HVES1_HVIL_Status":
						self.hvil_status_received.emit(int(self.st14.data[metric.name]))
					case "HVES1_Fast_Update_State_of_Charge":
						self.soc_received.emit(float(self.st14.data[metric.name]))
					case "HVES1_Available_Discharge_Power":
						self.discharge_power_received.emit(float(self.st14.data[metric.name]))				
					case "HVES1_Available_Charge_Power":
						self.charge_power_received.emit(float(self.st14.data[metric.name]))

		except Exception as e:
			print(f"Failed to decode message: {e}")


	def update_bus_voltage_field(self, val):
		self.bus_voltage_field.setText(f"{val:.2f} V")
		self.bus_voltage_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_battery_voltage_field(self, val):
		self.battery_voltage_field.setText(f"{val:.2f} V")
		self.battery_voltage_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_current_field(self, val):
		self.current_field.setText(f"{val:.2f} A")
		self.current_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_min_cell_voltage_field(self, val):
		self.min_cell_voltage_field.setText(f"{val:.2f} V")
		self.min_cell_voltage_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_max_cell_voltage_field(self, val):
		self.max_cell_voltage_field.setText(f"{val:.2f} V")
		self.max_cell_voltage_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_min_cell_temp_field(self, val):
		self.min_cell_temp_field.setText(f"{val:.2f} °C")
		self.min_cell_temp_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_max_cell_temp_field(self, val):
		self.max_cell_temp_field.setText(f"{val:.2f} °C")
		self.max_cell_temp_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_inlet_temp_field(self, val):
		self.inlet_temp_field.setText(f"{val:.2f} °C")
		self.inlet_temp_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_outlet_temp_field(self, val):
		self.outlet_temp_field.setText(f"{val:.2f} °C")
		self.outlet_temp_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_op_status_field(self, val):
		self.op_status_field.setText(f"{val}")
		self.op_status_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_bus_status_field(self, val):
		self.bus_status_field.setText(f"{val}")
		self.bus_status_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_hvil_status_field(self, val):
		self.hvil_status_field.setText(f"{val}")
		self.hvil_status_field.setAlignment(QtCore.Qt.AlignCenter)
		
	def update_soc_field(self, val):
		self.soc_field.setText(f"{val:.2f} %")
		self.soc_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_charge_power_field(self, val):
		self.charge_power_field.setText(f"{val:.2f} W")
		self.charge_power_field.setAlignment(QtCore.Qt.AlignCenter)

	def update_discharge_power_field(self, val):
		self.discharge_power_field.setText(f"{val:.2f} W")
		self.discharge_power_field.setAlignment(QtCore.Qt.AlignCenter)

if __name__ == "__main__":	
	app = QtWidgets.QApplication(sys.argv)
	window = MyApp()
	window.show()
	sys.exit(app.exec_())
	