from message import Message
from machine import UART

def test_calculate_checksum():
    print("\n=== Testing calculate_checksum ===")
    payload = [0x12, 0x34, 0x56, 0x78]
    checksum = Message.calculate_checksum(payload)
    print(f"Payload: {payload}")
    print(f"Calculated checksum: {checksum}")


def test_verify_checksum():
    print("\n=== Testing verify_checksum ===")
    payload = [0x12, 0x34, 0x56, 0x78]
    checksum = Message.calculate_checksum(payload)
    is_valid = Message.verify_checksum(payload, checksum)
    print(f"Payload: {payload}, Checksum: {checksum}, Verified: {is_valid}")


def test_parse():
    print("\n=== Testing parse ===")
    header = [0xAA, 0xAA]
    id = 0x12
    control = 0x03
    params = [0x01, 0x02, 0x03]
    length = 1 + 1 + len(params) + 1
    payload = [id, control] + params
    checksum = Message.calculate_checksum(payload)
    message_bytes = bytes(header + [length] + payload + [checksum])

    print(f"Message bytes to parse: {list(message_bytes)}")
    message = Message.parse(message_bytes)

    if message:
        print(f"Parsed message successfully: {vars(message)}")
    else:
        print("Failed to parse message")


def test_read(uart):
    print("\n=== Testing read ===")
    print("Waiting for a message on UART...")
    message = Message.read(uart)
    if message:
        print(f"Message read successfully: {vars(message)}")
    else:
        print("No message read")


def main():
    print("\n=== Running tests on Pico ===")
    test_calculate_checksum()
    test_verify_checksum()
    test_parse()

    # Test read med UART
    try:
        uart = UART(0, baudrate=115200, tx=0, rx=1)  # Justera pinnar och baudrate efter din setup
        test_read(uart)
    except Exception as e:
        print(f"UART error: {e}")


if __name__ == "__main__":
    main()

