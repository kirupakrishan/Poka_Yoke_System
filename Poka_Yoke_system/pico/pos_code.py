from umqtt.simple import MQTTClient
from machine import Pin
import utime
import network
from mfrc522 import MFRC522

wifi_ssid = "Kirupa"
wifi_password = "kushal0807"
mqtt_broker = "192.168.137.163"  # Usually localhost for local testing
unauthentry=False

client_id = "pico_client"
topic = b"my_topic"

client = MQTTClient(client_id, mqtt_broker)

RLed =Pin(18,Pin.OUT)
GLed =Pin(19,Pin.OUT)
RLed.value(0)
GLed.value(0)

# Create a map between keypad buttons and characters
matrix_keys = [['1', '2', '3', 'A'],
               ['4', '5', '6', 'B'],
               ['7', '8', '9', 'C'],
               ['*', '0', '#', 'D']]
# PINs according to schematic - Change the pins to match with your connections
keypad_rows = [11,10,9,8]
keypad_columns = [15,14,13,12]
# Create two empty lists to set up pins ( Rows output and columns input )
col_pins = []
row_pins = []
guess = []
#our secret pin, shhh do not tell anyone
secret_pin = ['0','0','0','0','0','0']
for x in range(0,4):
    row_pins.append(Pin(keypad_rows[x], Pin.OUT))
    row_pins[x].value(1)
    col_pins.append(Pin(keypad_columns[x], Pin.IN, Pin.PULL_DOWN))
    col_pins[x].value(0)
    
##############################Scan keys ####################
def scankeys(action):
    for row in range(4):
        for col in range(4): 
            row_pins[row].high()
            key = None
            if col_pins[col].value() == 1:
                print(matrix_keys[row][col],end='')
                key_press = matrix_keys[row][col]
                utime.sleep(0.3)
                guess.append(key_press)
            if len(guess) == 6:
                checkPin(guess,action)
                break
        row_pins[row].low()
##############################To check Pin #################
def checkPin(guess,action):
    if guess == secret_pin:
        print("\nYou got the secret pin correct")
        msg = f'{{"action":"{action}","pass":"{"".join(guess)}"}}'
        client.publish(topic, msg)
        print("Published:", msg)
        GLed.value(1)
        utime.sleep(3)
        GLed.value(0)
    else:   
        rc522 = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0)
        print("")
        print("Place the RFID Card")
        print("")
        while True:
            (stat, tag_type) = rc522.request(rc522.REQALL)
            if stat == rc522.OK:
                (status, raw_uid) = rc522.SelectTagSN()
                if stat == rc522.OK:
                    rfid_data = "{:02x}".format(raw_uid[0])
                    print("Card detected! UID: {}".format(rfid_data))
                    if rfid_data == "73":
                        msg = f'{{"action":"{action}","pass":"{rfid_data}"}}'
                        client.publish(topic, msg)
                        print("Published:", msg)
                        break
                    else:
                        msg = f'{"action":"Unauthorized {action[:-4]}"}'
                        client.publish(topic, msg)
                        print("Published:", msg)
                        global unauthentry
                        unauthentry = True
                        break


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    while not wlan.isconnected():
        pass

def main():
    global guess
    global unauthentry
    while True:
        print("Login :----------------")
        print("Enter the secret Pin")
        while True:
            if len(guess)==6:
                print("1")
                break
            scankeys("Login Pin")
        if(unauthentry):
            unauthentry=False
            guess=[]
            continue
        guess = []
        print("Logout :----------------")
        print("Enter the secret Pin")
        while True:
            if len(guess)==6:
                break
            scankeys("Logout Pin")
        guess = []
#         print("Logout :----------------")
#         print("Enter the secret Pin")
#         scankeys("Logout Pin")

if __name__ == "__main__":
    connect_wifi()
    client.connect()
    print("Connected to MQTT broker")
    main()


#Use MQTT to transfer data to server
