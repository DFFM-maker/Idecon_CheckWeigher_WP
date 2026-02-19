#!/usr/bin/env python3
"""
IDECON Client Python - Strutture Dati Complete
Test e validazione protocollo IDECON v2.7
"""

import socket
import select
import time
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Tuple
from enum import IntEnum

# Configurazione default
IDEON_IP = '172.16.224.210'
IDEON_PORT = 50000


class MotorRunning(IntEnum):
    """Stato motori nastri trasportatori"""
    STOPPED = 0
    ADJUSTMENT = 1
    OPERATIONAL = 2
    POWER_SAVING = 3
    RESTART_POWER_SAVING = 4


class WorkMode(IntEnum):
    """Modalità lavoro pesatrice"""
    LOCAL = 1
    REMOTE = 2
    MAINTENANCE = 3


class EventCode(IntEnum):
    """Codici evento IDECON"""
    ERRORS_RESET = 1000
    RECIPE_CHANGE_ACTIVE = 1001
    RECIPE_CHANGE_NOT_POSSIBLE = 1002
    MODIFIED_RECIPE = 1003
    BATCH_OPENING = 1004
    BATCH_CLOSURE = 1005
    BATCH_CHANGE = 1006
    MODIFIED_BATCH = 1007
    COMMAND_NOT_RECOGNIZED = 1008
    METAL_TEST_PERFORMED = 1009
    MODIFICATION_GENERAL_SETUP = 1010
    COMMAND_NOT_REMOTE_MODE = 1011
    MODE_CHANGE = 1012
    MODIFICATION_ALARMS_DEACTIVATED = 1013
    MODIFICATION_ALARMS_STOP = 1014
    MODIFICATION_EJECTORS = 1015
    SHUTDOWN_UPS = 1016


class MsgFilterBits(IntEnum):
    """Bit maschera MSGFILTER"""
    RESPONSES = 0      # Bit 0: Solo risposte
    ERRORS = 1         # Bit 1: Errori
    EVENTS = 2         # Bit 2: Eventi
    STATISTICS = 3     # Bit 3: Statistiche
    WEIGHTS = 4        # Bit 4: Pesi individuali
    IMPORTANT = 5      # Bit 5: Messaggi importanti


@dataclass
class IdeconWeightData:
    """Dati pesata individuale WEIGHT"""
    timestamp: str = ""
    production_order: str = ""
    batch_code: str = ""
    recipe_name: str = ""
    line_code: str = ""
    serial_number: str = ""
    weight_mg: int = 0
    delta_mg: int = 0
    classification: int = 0
    
    # Flags decodificati (19 bit)
    flag_product_too_long: bool = False
    flag_product_too_short: bool = False
    flag_metal: bool = False
    flag_weight_plus_plus: bool = False
    flag_weight_plus: bool = False
    flag_weight_minus_minus: bool = False
    flag_weight_minus: bool = False
    flag_weight_ok: bool = False
    flag_expelled: bool = False
    flag_product_too_close: bool = False
    flag_new_dynamic_tare: bool = False
    flag_incorrect_tare: bool = False
    flag_above_max_capacity: bool = False
    flag_below_min_capacity: bool = False
    flag_ok_minus_accepted: bool = False
    flag_no_upstream_consent: bool = False
    flag_invalid_preweight: bool = False
    flag_ok_above_nominal: bool = False
    flag_ok_below_nominal: bool = False
    
    @property
    def weight_g(self) -> float:
        return self.weight_mg / 1000.0
    
    @property
    def delta_g(self) -> float:
        return self.delta_mg / 1000.0
    
    def decode_classification(self):
        """Decodifica i 19 bit della classificazione"""
        cls = self.classification
        self.flag_product_too_long = bool(cls & (1 << 0))
        self.flag_product_too_short = bool(cls & (1 << 1))
        self.flag_metal = bool(cls & (1 << 2))
        self.flag_weight_plus_plus = bool(cls & (1 << 3))
        self.flag_weight_plus = bool(cls & (1 << 4))
        self.flag_weight_minus_minus = bool(cls & (1 << 5))
        self.flag_weight_minus = bool(cls & (1 << 6))
        self.flag_weight_ok = bool(cls & (1 << 7))
        self.flag_expelled = bool(cls & (1 << 8))
        self.flag_product_too_close = bool(cls & (1 << 9))
        self.flag_new_dynamic_tare = bool(cls & (1 << 10))
        self.flag_incorrect_tare = bool(cls & (1 << 11))
        self.flag_above_max_capacity = bool(cls & (1 << 12))
        self.flag_below_min_capacity = bool(cls & (1 << 13))
        self.flag_ok_minus_accepted = bool(cls & (1 << 14))
        self.flag_no_upstream_consent = bool(cls & (1 << 15))
        self.flag_invalid_preweight = bool(cls & (1 << 16))
        self.flag_ok_above_nominal = bool(cls & (1 << 17))
        self.flag_ok_below_nominal = bool(cls & (1 << 18))
    
    def get_active_flags(self) -> List[str]:
        """Restituisce lista dei flag attivi"""
        flags = []
        if self.flag_expelled: flags.append("EXPELLED")
        if self.flag_weight_ok: flags.append("OK")
        if self.flag_weight_plus: flags.append("+")
        if self.flag_weight_plus_plus: flags.append("++")
        if self.flag_weight_minus: flags.append("-")
        if self.flag_weight_minus_minus: flags.append("--")
        if self.flag_metal: flags.append("METAL")
        if self.flag_ok_below_nominal: flags.append("OK-")
        if self.flag_ok_above_nominal: flags.append("OK+")
        return flags
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'production_order': self.production_order,
            'batch_code': self.batch_code,
            'recipe_name': self.recipe_name,
            'line_code': self.line_code,
            'serial_number': self.serial_number,
            'weight_mg': self.weight_mg,
            'weight_g': self.weight_g,
            'delta_mg': self.delta_mg,
            'delta_g': self.delta_g,
            'classification': hex(self.classification),
            'flags': self.get_active_flags()
        }


@dataclass
class IdeconStatPData:
    """Statistiche produzione STATP (50 campi)"""
    # Campi base (1-7)
    timestamp: str = ""
    batch_start_datetime: str = ""
    production_order: str = ""
    production_code: str = ""
    recipe_name: str = ""
    line_code: str = ""
    serial_number: str = ""
    
    # Global batch (8-26)
    total_products: int = 0
    total_accepted: int = 0
    avg_weight_accepted: float = 0.0
    min_weight_accepted: float = 0.0
    max_weight_accepted: float = 0.0
    rejected_minus: int = 0
    rejected_minus_minus: int = 0
    rejected_plus: int = 0
    rejected_plus_plus: int = 0
    cannot_be_weighed: int = 0
    metal_category: int = 0
    
    # Metal test (19-22)
    metal_tests_performed: int = 0
    metal_tests_passed: int = 0
    metal_tests_failed: int = 0
    metal_tests_refused: int = 0
    
    # Last weight (23-26)
    last_weight_exact: float = 0.0
    last_weight_rounded: float = 0.0
    last_weight_diff: float = 0.0
    last_weight_class: str = ""
    
    # Incremental (27-46)
    incremental_products: int = 0
    incremental_accepted: int = 0
    incremental_datetime: str = ""
    incremental_avg_weight: float = 0.0
    incremental_min_weight: float = 0.0
    incremental_max_weight: float = 0.0
    incremental_rejected_minus: int = 0
    incremental_rejected_minus_minus: int = 0
    incremental_rejected_plus: int = 0
    incremental_rejected_plus_plus: int = 0
    incremental_cannot_be_weighed: int = 0
    incremental_metal_category: int = 0
    incremental_metal_tests_performed: int = 0
    incremental_metal_tests_passed: int = 0
    incremental_metal_tests_failed: int = 0
    incremental_metal_tests_refused: int = 0
    incremental_last_weight_exact: float = 0.0
    incremental_last_weight_rounded: float = 0.0
    incremental_last_weight_diff: float = 0.0
    incremental_last_weight_class: str = ""
    
    # Altri (47-50)
    user_name: str = ""
    total_ok_minus: int = 0
    total_ok_minus_accepted: int = 0
    standard_deviation: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass  
class IdeconEventData:
    """Dati evento EVENT"""
    timestamp: str = ""
    production_order: str = ""
    batch_code: str = ""
    recipe_name: str = ""
    line_code: str = ""
    serial_number: str = ""
    event_code: int = 0
    event_description: str = ""
    operator: str = ""
    
    @property
    def event_name(self) -> str:
        """Restituisce nome evento da codice"""
        try:
            return EventCode(self.event_code).name
        except:
            return f"UNKNOWN_{self.event_code}"
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'production_order': self.production_order,
            'batch_code': self.batch_code,
            'recipe_name': self.recipe_name,
            'line_code': self.line_code,
            'serial_number': self.serial_number,
            'event_code': self.event_code,
            'event_name': self.event_name,
            'event_description': self.event_description,
            'operator': self.operator
        }


@dataclass
class IdeconStatus:
    """Stato macchina da STATSV"""
    status_code: str = ""  # 8 caratteri
    motor_status: int = 0  # Pos 1: 0-4
    production_started: bool = False  # Pos 2
    has_errors: bool = False  # Pos 3
    has_warnings: bool = False  # Pos 4
    has_messages: bool = False  # Pos 5
    stats_enabled: bool = False  # Pos 6
    work_mode: int = 1  # Pos 7: 1-3
    connection_status: int = 0  # Pos 8
    
    @property
    def motor_running(self) -> MotorRunning:
        return MotorRunning(self.motor_status)
    
    @property
    def work_mode_enum(self) -> WorkMode:
        return WorkMode(self.work_mode)
    
    def decode(self, status_str: str):
        """Decodifica stringa STATSV (es: '20110011')"""
        if len(status_str) >= 8:
            self.status_code = status_str
            self.motor_status = int(status_str[0])
            self.production_started = status_str[1] == '1'
            self.has_errors = status_str[2] == '1'
            self.has_warnings = status_str[3] == '1'
            self.has_messages = status_str[4] == '1'
            self.stats_enabled = status_str[5] == '1'
            self.work_mode = int(status_str[6])
            self.connection_status = int(status_str[7])
    
    def to_dict(self) -> dict:
        return {
            'status_code': self.status_code,
            'motor_running': self.motor_running.name,
            'production_started': self.production_started,
            'has_errors': self.has_errors,
            'has_warnings': self.has_warnings,
            'has_messages': self.has_messages,
            'stats_enabled': self.stats_enabled,
            'work_mode': self.work_mode_enum.name,
            'connection_status': self.connection_status
        }


class IdeconClient:
    """Client TCP per comunicazione con IDECON"""
    
    def __init__(self, ip: str = IDEON_IP, port: int = IDEON_PORT):
        self.ip = ip
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.msg_filter = 17  # Default: risposte + pesi
        self.last_error = ""
        self.stats = {
            'weights_received': 0,
            'events_received': 0,
            'statp_received': 0,
            'commands_sent': 0,
            'errors': 0
        }
    
    def connect(self, timeout: float = 10.0) -> bool:
        """Connessione alla bilancia"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)
            self.socket.connect((self.ip, self.port))
            self.connected = True
            return True
        except Exception as e:
            self.last_error = str(e)
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnessione"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False
    
    def send_command(self, command: str, timeout: float = 5.0) -> Tuple[bool, str]:
        """Invia comando e attende risposta"""
        if not self.connected or not self.socket:
            return False, "Not connected"
        
        try:
            # Costruisci messaggio STX+cmd+ETX
            msg = b'\x02' + command.encode('ascii') + b'\x03'
            self.socket.sendall(msg)
            self.stats['commands_sent'] += 1
            
            # Attendi risposta
            self.socket.settimeout(timeout)
            response = self.socket.recv(512)
            
            if response:
                # Rimuovi STX e ETX
                if response[0] == 0x02:
                    response = response[1:]
                if response[-1] == 0x03:
                    response = response[:-1]
                
                return True, response.decode('ascii', errors='replace')
            
            return False, "No response"
            
        except socket.timeout:
            return False, "Timeout"
        except Exception as e:
            self.stats['errors'] += 1
            return False, str(e)
    
    def set_msg_filter(self, filter_value: int) -> bool:
        """Imposta MSGFILTER"""
        success, response = self.send_command(f"MSGFILTER={filter_value}")
        if success and "MSGFILTER" in response:
            self.msg_filter = filter_value
            return True
        return False
    
    def get_status(self) -> Optional[IdeconStatus]:
        """Richiede STATSV"""
        success, response = self.send_command("STATSV")
        if success and response.startswith("STATSV="):
            status = IdeconStatus()
            status.decode(response[7:])
            return status
        return None
    
    def parse_weight(self, message: str) -> Optional[IdeconWeightData]:
        """Parsa messaggio WEIGHT"""
        if not message.startswith("WEIGHT="):
            return None
        
        try:
            data = message[7:]  # Rimuovi WEIGHT=
            parts = data.split("|")
            
            if len(parts) < 9:
                return None
            
            weight = IdeconWeightData(
                timestamp=parts[0],
                production_order=parts[1],
                batch_code=parts[2],
                recipe_name=parts[3],
                line_code=parts[4],
                serial_number=parts[5],
                weight_mg=int(parts[6]),
                delta_mg=int(parts[7]),
                classification=int(parts[8], 16) if parts[8] else 0
            )
            
            weight.decode_classification()
            self.stats['weights_received'] += 1
            return weight
            
        except Exception as e:
            self.stats['errors'] += 1
            return None
    
    def parse_event(self, message: str) -> Optional[IdeconEventData]:
        """Parsa messaggio EVENT"""
        if not message.startswith("EVENT="):
            return None
        
        try:
            data = message[6:]  # Rimuovi EVENT=
            parts = data.split("|")
            
            if len(parts) < 8:
                return None
            
            # Estrai codice evento da "Cod. XXXX"
            event_code_str = parts[6].replace("Cod.", "").strip()
            event_code = int(event_code_str)
            
            event = IdeconEventData(
                timestamp=parts[0],
                production_order=parts[1],
                batch_code=parts[2],
                recipe_name=parts[3],
                line_code=parts[4],
                serial_number=parts[5],
                event_code=event_code,
                event_description=parts[7],
                operator=parts[8] if len(parts) > 8 else ""
            )
            
            self.stats['events_received'] += 1
            return event
            
        except Exception as e:
            self.stats['errors'] += 1
            return None


if __name__ == "__main__":
    # Test base
    print("="*70)
    print("IDECON Client Python - Test Strutture Dati")
    print("="*70)
    
    # Test Weight Data
    print("\n[TEST] IdeconWeightData")
    weight = IdeconWeightData(
        timestamp="2026.02.10 13:22:42:773",
        production_order="ordine123",
        batch_code="BATCH001",
        recipe_name="225g",
        line_code="Linea1",
        serial_number="ID02792",
        weight_mg=224700,
        delta_mg=700,
        classification=0x20480
    )
    weight.decode_classification()
    
    print(f"Peso: {weight.weight_g:.3f}g")
    print(f"Delta: {weight.delta_g:+.3f}g")
    print(f"Flags attivi: {weight.get_active_flags()}")
    print(f"JSON: {json.dumps(weight.to_dict(), indent=2)}")
    
    # Test Status
    print("\n[TEST] IdeconStatus")
    status = IdeconStatus()
    status.decode("20110011")
    print(f"Status Code: {status.status_code}")
    print(f"Motor: {status.motor_running.name}")
    print(f"Work Mode: {status.work_mode_enum.name}")
    print(f"Has Errors: {status.has_errors}")
    
    print("\n" + "="*70)
    print("Test completato!")
    print("="*70)