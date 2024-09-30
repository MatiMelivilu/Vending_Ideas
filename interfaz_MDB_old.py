import tkinter as tk
import serial
import threading
import socket
import subprocess
import os
import signal
import sys
import datetime
import time

#Numero serial unico de raspberry
SERIAL_NUMBER = "100000007ccad951"
#estado de control para el uso de boton
STATE = 0
TIMEOUT = 0
POS_CONNECT = 0

U_VENTA = "Rechazado"
EST_U_VENTA = 0
LAST_MESSAGE = "0707"

#Parametros extraidos de .txt
PARAMETROS={}
#Rutas de conexion serial de gpio y boton
#ruta_serial = '/dev/ttyS0'
#ruta_boton  = '/dev/ttyUSB0'

class SerialGUI(tk.Tk):
    
    def __init__(self, log_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global PARAMETROS
        global POS_CONNECT
        ruta_serial = PARAMETROS.get('ruta_serial', None)
        ruta_boton = PARAMETROS.get('ruta_boton', None)

        self.serial_port = serial.Serial(ruta_serial, 9600, timeout=0.1)
        
        
        if (self.dispositivo_conectado(ruta_boton)):
                self.serial_port2 = serial.Serial(ruta_boton, 9600, timeout=0.1)
                print('boton conectado')
        else:
                print('no hay boton')
                
        
        self.log_file = log_file
        self.title("MDB control")
        self.geometry("550x350")

        self.message_log = tk.Text(self, height=10, width=50)
        self.message_log.pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        send_button1 = tk.Button(button_frame, text="Nivel 1", command=self.send_message1)
        send_button1.grid(row=0, column=0, padx=5)

        send_button2 = tk.Button(button_frame, text="Nivel 2", command=self.send_message2)
        send_button2.grid(row=0, column=1, padx=5)

        send_button3 = tk.Button(button_frame, text="Nivel 3", command=self.send_message3)
        send_button3.grid(row=0, column=2, padx=5)

        send_button4 = tk.Button(button_frame, text="Begin session", command=self.send_message4)
        send_button4.grid(row=0, column=3, padx=5)
        
        send_button5 = tk.Button(button_frame, text="Carga llaves", command=self.send_message5)
        send_button5.grid(row=1, column=0, padx=5)
        
        send_button6 = tk.Button(button_frame, text="Cierre de caja", command=self.send_message6)
        send_button6.grid(row=1, column=1, padx=5)
        
        send_button7 = tk.Button(button_frame, text="Inicialización", command=self.send_message7)
        send_button7.grid(row=1, column=2, padx=5)
        
        send_button8 = tk.Button(button_frame, text="ulima venta", command=self.send_message8)
        send_button8.grid(row=1, column=3, padx=5)
        
        send_button9 = tk.Button(button_frame, text="Poll", command=self.send_message9)
        send_button9.grid(row=2, column=0, padx=5)
        
        send_button10 = tk.Button(button_frame, text="respuesta ini.", command=self.send_message10)
        send_button10.grid(row=2, column=1, padx=5)
        
        send_button11 = tk.Button(button_frame, text="cancelar ult. venta", command=self.send_message11)
        send_button11.grid(row=2, column=2, padx=5)
        
        send_button12 = tk.Button(button_frame, text="07", command=self.send_message12)
        send_button12.grid(row=3, column=0, padx=5)
        
        send_button13 = tk.Button(button_frame, text="06", command=self.send_message13)
        send_button13.grid(row=3, column=1, padx=5)
        
        send_button14 = tk.Button(button_frame, text="05", command=self.send_message14)
        send_button14.grid(row=3, column=2, padx=5)
        
        send_button15 = tk.Button(button_frame, text="04", command=self.send_message15)
        send_button15.grid(row=3, column=3, padx=5)
        
        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()
        
    def dispositivo_conectado(self, ruta):
            return os.path.exists(ruta)

    def POS(self, precio_hex, item_hex):
        X = 1
        Y = 0
        precio = int(precio_hex.hex(), 16)
        P_actual = precio * X * (10 ** (-1 * Y))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("01" +  str(P_actual)).encode())
        respuesta = client_socket.recv(1024).decode()
        client_socket.close()
        return respuesta 
        
    def cargar_llaves(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("02").encode())
        respuesta = client_socket.recv(1024).decode()
        self.message_log.insert(tk.END, "Carga de llaves: " + respuesta + "\n")
        self.log_file.write("Carga de llaves: " + respuesta + "\n")
        self.log_file.flush()
        client_socket.close()
        return respuesta 
        
    def cierre_caja(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("03").encode())
        respuesta = client_socket.recv(1024).decode()
        self.message_log.insert(tk.END, "Cierre de caja: " + respuesta + "\n")
        self.log_file.write("Cierre de caja: " + respuesta + "\n")
        self.log_file.flush()
        client_socket.close()
        return respuesta 
        
    def init(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("04").encode())
        respuesta = client_socket.recv(1024).decode()
        self.message_log.insert(tk.END, "Inicialización: " + respuesta + "\n")
        self.log_file.write("Inicialización: " + respuesta + "\n")
        self.log_file.flush()
        client_socket.close()
        return respuesta 
        
    def ultima_venta(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("05").encode())
        respuesta = client_socket.recv(1024).decode()
        self.message_log.insert(tk.END, "Ultima venta: " + respuesta + "\n")
        self.log_file.write("Ultima venta: " + respuesta + "\n")
        self.log_file.flush()
        client_socket.close()
        return respuesta 
        
    def Poll(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("06").encode())
        respuesta = client_socket.recv(1024).decode()
        self.message_log.insert(tk.END, "Poll: " + respuesta + "\n")
        self.log_file.write("Poll: " + respuesta + "\n")
        self.log_file.flush()
        client_socket.close()
        return respuesta 
        
    def respuesta_inicializacion(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("07").encode())
        respuesta = client_socket.recv(1024).decode()
        self.message_log.insert(tk.END, "respuesta inicializacion: " + respuesta + "\n")
        self.log_file.write("respuesta inicializacion: " + respuesta + "\n")
        self.log_file.flush()
        client_socket.close()
        return respuesta 
        
    def devolucion(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("08").encode())
        respuesta = client_socket.recv(1024).decode()
        self.message_log.insert(tk.END, "respuesta devolucion ult. venta: " + respuesta + "\n")
        self.log_file.write("respuesta devolucion ult. venta: " + respuesta + "\n")
        self.log_file.flush()
        client_socket.close()
        return respuesta 
        
    def control_message(self, mensaje):
        mensaje = mensaje.lstrip('0')
        if len(mensaje) % 2 != 0:
            mensaje += '0'
            
        mensaje_bytes = bytes.fromhex(mensaje)
        ID = mensaje_bytes[0:2]
        ID_hex = ID.hex()
        largo = len(mensaje_bytes)
        print('el largo de bytes es: ',largo)
        global STATE
        global TIMEOUT
        global U_VENTA
        global EST_U_VENTA
        global LAST_MESSAGE
        
        if ((ID_hex == "1300" or ID_hex == "1306")  and EST_U_VENTA == 0):
            TIMEOUT = 1
            EST_U_VENTA = 1
            precio_hex = mensaje_bytes[2:4]
            item_hex = mensaje_bytes[4:6]
          
            pago = self.POS(precio_hex, item_hex)
            self.message_log.insert(tk.END, "POS: " + pago + "\n")
            self.log_file.write("POS: " + pago + "\n")
            self.log_file.flush()
            
            U_VENTA = pago
            
            if pago == 'Aprobado':
                respuesta = bytes.fromhex('05') + precio_hex
                checksum = sum(respuesta) & 0xFF
                enviar = respuesta + bytes([checksum])
                LAST_MESSAGE = enviar.hex()
                self.send_serial_message(enviar)
                
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                log = f"{current_time} READER: {enviar.hex()}\n"
                
                self.message_log.insert(tk.END, log)
                self.log_file.write(log)
                
                self.log_file.flush()
                
                
            else:
                enviar = bytes.fromhex('0606')
                self.send_serial_message(enviar)
                
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                log = f"{current_time} READER: {enviar.hex()}\n"
                
                self.message_log.insert(tk.END, log)
                self.log_file.write(log)
                
                self.log_file.flush()
                
        elif (ID_hex == "1300" and EST_U_VENTA == 1):
            
            if U_VENTA == 'Aprobado':
                enviar = bytes.fromhex(LAST_MESSAGE) 
                
                self.send_serial_message(enviar)
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                log = f"{current_time} READER: {enviar.hex()}\n"
                
                self.message_log.insert(tk.END, log)
                self.log_file.write(log)
                
                self.log_file.flush()
                
            else:
                enviar = bytes.fromhex('0606')
                self.send_serial_message(enviar)
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                log = f"{current_time} READER: {enviar.hex()}\n"
                
                self.message_log.insert(tk.END, log)
                self.log_file.write(log)
                
                self.log_file.flush()
                
        elif (ID_hex == "1301" and largo == 3):
            enviar = bytes.fromhex('0606')
            self.send_serial_message(enviar)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            log = f"{current_time} READER: {enviar.hex()}\n"
                
            self.message_log.insert(tk.END, log)
            self.log_file.write(log)
                
            self.log_file.flush()
            #STATE = 0 
            #TIMEOUT=0

            
        elif (ID_hex == "1302"):
            LAST_MESSAGE = "0707"
            if ('130417' in mensaje):
                enviar = bytes.fromhex('0707')
                self.send_serial_message(enviar)
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                log = f"{current_time} READER: {enviar.hex()}\n"
                
                self.message_log.insert(tk.END, log)
                self.log_file.write(log)
                
                self.log_file.flush()
                #time.sleep(1)
                STATE = 0
                TIMEOUT=0
                EST_U_VENTA = 0
                LAST_MESSAGE = "0707"
            else:
                pass
            
        elif (ID_hex == "1303"):
            if ('130417' in mensaje):
                enviar = bytes.fromhex('0707')
                self.send_serial_message(enviar)
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                log = f"{current_time} READER: {enviar.hex()}\n"
                
                self.message_log.insert(tk.END, log)
                self.log_file.write(log)
                
                self.log_file.flush()
                #time.sleep(1)
                STATE = 0
                TIMEOUT=0 
                EST_U_VENTA = 0
                LAST_MESSAGE = "0707"
            else:
                pass

        elif (ID_hex == "1304" and largo == 3):
            time.sleep(0.5)
            enviar = bytes.fromhex('0707')
            self.send_serial_message(enviar)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            log = f"{current_time} READER: {enviar.hex()}\n"
                
            self.message_log.insert(tk.END, log)
            self.log_file.write(log)
                
            self.log_file.flush()
            time.sleep(0.5)
            STATE = 0 
            TIMEOUT=0
            EST_U_VENTA = 0
            LAST_MESSAGE = "0707"
                    
        elif (ID_hex == "1305" and largo == 7):
                pass
   
        elif (ID_hex == "1307" and largo == 6):
            enviar = bytes.fromhex('0000')
            self.send_serial_message(enviar)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            log = f"{current_time} READER: {enviar.hex()}\n"
                
            self.message_log.insert(tk.END, log)
            self.log_file.write(log)
                
            self.log_file.flush()
            
        elif (ID_hex == "1400" and largo ==3):
                pass
               
        elif (ID_hex == "1401" and largo == 3):
            if ('140115' in mensaje):
                pass
                #enviar = bytes.fromhex('0707')
                #self.send_serial_message(enviar)
                #self.message_log.insert(tk.END, "Enviado: " + enviar.hex() + "\n")
                #self.log_file.write("Enviado: " + enviar.hex() + "\n")
                #self.log_file.flush()
                #time.sleep(1)
                #STATE = 0
                #TIMEOUT=0 
            else:
                pass
               
        elif (ID_hex == "1402" and largo == 3):
            enviar = bytes.fromhex('0808')
            self.send_serial_message(enviar)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            log = f"{current_time} READER: {enviar.hex()}\n"
                
            self.message_log.insert(tk.END, log)
            self.log_file.write(log)
                
            self.log_file.flush()
               
        elif (ID_hex == "1403"):
                pass
            
        elif (ID_hex == "1500"):
            enviar = bytes.fromhex('0D0D')
            self.send_serial_message(enviar)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            log = f"{current_time} READER: {enviar.hex()}\n"
                
            self.message_log.insert(tk.END, log)
            self.log_file.write(log)
                
            self.log_file.flush()
            
        elif (ID_hex == "1501"):
            enviar = bytes.fromhex('0FFFFF0D') #0D0D para aprobar y 0E0E para denegar
            self.send_serial_message(enviar)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            log = f"{current_time} READER: {enviar.hex()}\n"
                
            self.message_log.insert(tk.END, log)
            self.log_file.write(log)
                
            self.log_file.flush()
               
    def send_message1(self):
        message = '0101115201003C01A3'
        self.send_serial_message(bytes.fromhex(message))
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        log = f"{current_time} READER: {message}\n"
                
        self.message_log.insert(tk.END, log)
        self.log_file.write(log)
                
        self.log_file.flush()

    def send_message2(self):
        message = '0102115201003C01A4'
        self.send_serial_message(bytes.fromhex(message))
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        log = f"{current_time} READER: {message}\n"
                
        self.message_log.insert(tk.END, log)
        self.log_file.write(log)
                
        self.log_file.flush()

    def send_message3(self):
        message = '0103115201003C01A5'
        self.send_serial_message(bytes.fromhex(message))
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        log = f"{current_time} READER: {message}\n"
                
        self.message_log.insert(tk.END, log)
        self.log_file.write(log)
                
        self.log_file.flush()
        
    def send_message4(self):
        global PARAMETROS
        message = PARAMETROS.get('begin_sesion', None)
        self.send_serial_message(bytes.fromhex(message))
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        log = f"{current_time} READER: {message}\n"
                
        self.message_log.insert(tk.END, log)
        self.log_file.write(log)
                
        self.log_file.flush()
        
    def send_message5(self):
        self.cargar_llaves()
        
    def send_message6(self):
        self.cierre_caja()
        
    def send_message7(self):
        self.init()
        
    def send_message8(self):
        self.ultima_venta()
        
    def send_message9(self):
        self.Poll()
   
    def send_message10(self):
        self.respuesta_inicializacion() 
        
    def send_message11(self):
        self.devolucion() 
        
    def send_message12(self):
        message = '0707'
        self.send_serial_message(bytes.fromhex(message))
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        log = f"{current_time} READER: {message}\n"
                
        self.message_log.insert(tk.END, log)
        self.log_file.write(log)
                
        self.log_file.flush()
        
    def send_message13(self):
        message = '0606'
        self.send_serial_message(bytes.fromhex(message))
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        log = f"{current_time} READER: {message}\n"
                
        self.message_log.insert(tk.END, log)
        self.log_file.write(log)
                
        self.log_file.flush()
        
    def send_message14(self):
        message = '05FFFF03'
        self.send_serial_message(bytes.fromhex(message))
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        log = f"{current_time} READER: {message}\n"
                
        self.message_log.insert(tk.END, log)
        self.log_file.write(log)
                
        self.log_file.flush()
        
    def send_message15(self):
        message = '0404'
        self.send_serial_message(bytes.fromhex(message))
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        log = f"{current_time} READER: {message}\n"
                
        self.message_log.insert(tk.END, log)
        self.log_file.write(log)
                
        self.log_file.flush()

    def send_serial_message(self, message):
        self.serial_port.write(message)
        
    def read_serial(self):
        global STATE
        global PARAMETROS
        global TIMEOUT
        global POS_CONNECT
        start_time = time.time()
        reset_time = time.time()
        boton_time = time.time()
        ruta_boton = PARAMETROS.get('ruta_boton', None)
        auto_begin = PARAMETROS.get('auto_begin', None)
        
        
        #self.pos_port = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        while True:
            elapsed_time = time.time() - start_time
            elreset_time = time.time() - reset_time
            elboton_time = time.time() - boton_time
            #print(elreset_time)

                                
            if (STATE == 1 and self.dispositivo_conectado(ruta_boton)):
                    if elapsed_time <= 0.5:
                            self.serial_port2.write(b'\x00')
                            
                    elif elapsed_time > 0.5 and elapsed_time <= 1:  
                            self.serial_port2.write(b'\xFF')
                    
                    elif elapsed_time > 1:
                            start_time = time.time()
                            elapsed_time = 0
                            self.serial_port2.reset_output_buffer()
                            self.serial_port2.reset_input_buffer()
            else: 
                    pass
              
            if(auto_begin == 'True' and STATE == 0):
                STATE = 1
                #time.sleep(0.1)  
                self.send_message4()
                reset_time = time.time()
                elreset_time = 0
                    
            if (self.serial_port.in_waiting > 0):
                received_data = self.serial_port.readline().decode().strip()
                received = ''.join(filter(lambda x: x in '0123456789abcdefABCDEF', received_data))
                
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                log = f"{current_time} VMC: {received}\n"
                
                self.message_log.insert(tk.END, log)
                self.log_file.write(log)
                self.log_file.flush()
                self.message_log.see(tk.END)
                self.control_message(received)
                #reincio de begin
                reset_time = time.time()
                elreset_time = 0
            else:
                if( (auto_begin == 'True') and (STATE == 1) and (TIMEOUT ==0)  ):
                    if elreset_time > 10:
                        self.send_message12()
                        time.sleep(0.1)
                        STATE = 0

            if (self.dispositivo_conectado(ruta_boton)):
                    if (self.serial_port2.in_waiting > 0 and STATE == 0):
                        STATE = 1
                        boton_time = time.time()
                        elboton_time = 0
                        self.serial_port2.reset_output_buffer()
                        self.serial_port2.reset_input_buffer()
                        self.send_message4()
                    else:
                        if (elboton_time >= 60 and STATE == 1):
                            STATE = 0
                            self.serial_port2.reset_output_buffer()
                            self.serial_port2.reset_input_buffer()
                            self.send_message12()
                            boton_time = time.time()
                            elboton_time = 0
            else:
                
                    pass            
            self.update_idletasks()

def handle_exit(signum, frame):
    if node_process.poll() is None:
        node_process.terminate()
    sys.exit()
    
def get_serial():
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    return line.split(":")[1].strip()
                    
    except:
        return None

#Manejo de parametros en archivo .txt

def leer_parametros(archivo):
    global PARAMETROS
    with open(archivo, 'r') as f:
        for linea in f:
            if '=' in linea:
                clave, valor = linea.strip().split('=', 1)
                PARAMETROS[clave]=valor
                
def modificar_parametros(clave, nuevo_valor):
    global PARAMETROS
    if clave in PARAMETROS:
        PARAMETROS[clave] = nuevo_valor
        return True
    return False
    
def escribir_parametros(archivo):
    global PARAMETROS
    with open(archivo, 'w') as f:
        for clave, valor in PARAMETROS.items():
            f.write(f'{clave}={valor}\n')

if __name__ == "__main__":
    #validacion serial
    serial_num = get_serial()
    
    if serial_num is None:
            print("Error en obtener datos")
            sys.exit(1)
            
    if serial_num != SERIAL_NUMBER:
            print("No compatible")
            sys.exit(1)
    
    #Apertura de archivo.txt
    archivo = 'parametros.txt'
    leer_parametros(archivo)
    
    # Ruta al programa Node.js
    node_program = "/home/IdeasDigitales/Desktop/control_Pago_POS_v2.js"

    # Verificar si el archivo Node.js existe
    if not os.path.exists(node_program):
        print("El programa Node.js no se encuentra en la ruta especificada.")
        exit()

    # Asociar la señal SIGINT (Ctrl+C) al manejador de salida
    signal.signal(signal.SIGINT, handle_exit)

    # Ejecutar el programa Node.js
    node_process = subprocess.Popen(["node", node_program])

    # Crear y mostrar la interfaz de usuario
    # Crear carpeta log si no existe
    if not os.path.exists("/home/IdeasDigitales/log"):
        os.makedirs("/home/IdeasDigitales/log")

    # Generar nombre de archivo de log
    log_filename = f"/home/IdeasDigitales/log/log_{datetime.datetime.now().strftime('%Y%m%d')}.txt"

    # Abrir archivo de log
    with open(log_filename, "a") as log_file:
        print("iniciando")
        app = SerialGUI(log_file)
        app.mainloop()

    # Si la interfaz se cierra, se termina el proceso de Node.js
    if node_process.poll() is None:
        node_process.terminate()


  
