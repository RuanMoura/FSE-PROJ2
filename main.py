import signal
import threading
import os
from time import sleep
from typing import Any
from datetime import datetime
from uart import UART_CLASS
from bme import BME_CLASS
from pwm import PWM_CLASS
from pid import PID_CLASS
from menu import MENU_CLASS

UART = UART_CLASS()
BME = BME_CLASS()
PWM = PWM_CLASS()
PID = PID_CLASS()
MENU = MENU_CLASS()

on_off: int = 0
operating: int = 0
curve: int = 0
ta: float = 0.0
ti: float = 0.0
tr: float = 0.0
control_signal: int = 0

index_curve: int = 0
count_curve: float = 0.0

def handle_ctrlc(signum, frame) -> None:
    turn_off()
    MENU.close()
    os._exit(0)


def try_get(function, last_value,  *params) -> Any:
    for _ in range(5):
        try:
            res = function(*params)
        except:
            continue
        if res != -1:
            return res
    return last_value


def control_temp() -> None:
    global ta, tr, ti, control_signal

    PID.atualiza_referencia(tr)
    control_signal = int(PID.controle(ti))
    UART.send_control_signal(control_signal)
    if control_signal >= 0:
        PWM.set_resistance(control_signal)
        PWM.set_fan(0)
    else:
        PWM.set_resistance(0)
        control_signal = min(control_signal, -40)
        PWM.set_fan(control_signal*-1)


def interact_dashbord():
    global on_off, operating, curve, control_signal
    user_input = try_get(UART.get_user_input, 0)
    if user_input == 0xA1:
        turn_on()
    elif user_input == 0xA2:
        turn_off()
    elif user_input == 0xA3:
        operating_on()
    elif user_input == 0xA4:
        operating_off()
    elif user_input == 0xA5:
        curve_mode()


def interact_terminal():
    global on_off, operating, curve, tr
    while True:
        res = MENU.interact()
        if not res:
            continue
        if res[0] == "on_off" and not on_off:
            turn_on()
        elif res[0] == "on_off" and on_off:
            turn_off()
        elif res[0] == "operating" and not operating:
            operating_on()
        elif res[0] == "operating" and operating:
            operating_off()
        elif res[0] == "curve":
            curve_mode()
        elif res[0] == "tr" and res[1] == "l" and not curve:
            tr = max(tr-5, 0)
            UART.send_reference_temperature(float(tr))
        elif res[0] == "tr" and res[1] == "r" and not curve:
            tr += 5
            UART.send_reference_temperature(float(tr))


def turn_on():
    global on_off
    UART.send_system_state(1)
    on_off = 1


def turn_off():
    global on_off, operating, curve, control_signal
    on_off = 0
    UART.send_system_state(0)
    operating = 0
    UART.send_operation_state(0)
    curve = 0
    UART.send_control_mode(0)
    control_signal = 0
    UART.send_control_signal(0)
    PWM.stop()


def operating_on():
    global on_off, operating
    if not on_off:
        turn_on()
    UART.send_operation_state(1)
    operating = 1
    PWM.start()


def operating_off():
    global operating, control_signal
    operating = 0
    UART.send_operation_state(0)
    control_signal = 0
    UART.send_control_signal(0)
    PWM.stop()


def curve_mode():
    global curve, index_curve, count_curve
    curve = (curve + 1) % 2
    UART.send_control_mode(curve)
    if curve:
        index_curve = 0
        count_curve = 0.0


def main() -> None:
    global ta, ti, tr, control_signal, on_off, operating, curve
    global index_curve, count_curve
    signal.signal(signal.SIGINT, handle_ctrlc)
    PID.configura_constantes(30.0, 0.2, 400.0)
    tr = try_get(UART.get_tr, tr)

    threading.Thread(target=interact_terminal).start()

    fp_log_csv = open("log.csv", "w")
    fp_log_csv.write("datetime, temp ambiente, temp interna, temp referencia, sinal controle\n")
    with open("curva_reflow.csv") as fp:
        curves = fp.readlines()[1:]
    current_time, current_reference = curves[index_curve][:-1].split(',')
    while True:
        ta = BME.get_temperature()
        UART.send_room_temperature(ta)
        ti = try_get(UART.get_ti, ti)

        if not curve:
            tr = try_get(UART.get_tr, tr)
        interact_dashbord()

        if curve:
            tr = float(current_reference)
            UART.send_reference_temperature(tr)
            count_curve += 0.5
            if count_curve > int(current_time):
                index_curve += 1
            if index_curve >= len(curves):
                curve = 0
            else:
                current_time, current_reference = curves[index_curve][:-1].split(',')
        if operating:
            control_temp()
        MENU.set_constant(
            tr, ti, ta, control_signal, on_off, operating, curve)

        fp_log_csv.write(f"{str(datetime.now())}, {ta}, {ti}, {tr}, {control_signal}\n")
        sleep(0.5)


if __name__ == "__main__":
    main()