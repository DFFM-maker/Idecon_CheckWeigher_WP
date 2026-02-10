#!/usr/bin/env python3
"""
IDECON Monitor CLI - Monitoraggio real-time pesate ed eventi
"""

import sys
import time
import select
import json
from datetime import datetime
from idecon_client import IdeconClient, IDEON_IP, IDEON_PORT

class IdeconMonitorCLI:
    """Monitor CLI per IDECON"""
    
    def __init__(self, ip: str = IDEON_IP, port: int = IDEON_PORT):
        self.client = IdeconClient(ip, port)
        self.running = False
        self.weights = []
        self.events = []
        self.show_json = False
        self.log_file = None
        
    def connect(self) -> bool:
        """Connessione alla bilancia"""
        print(f"\n[CONNessione] {self.client.ip}:{self.client.port}...")
        
        if self.client.connect():
            print("[OK] Connesso!")
            
            # Imposta MSGFILTER per ricevere pesi ed eventi
            print("[CONFIG] MSGFILTER=17 (risposte + pesi)")
            if self.client.set_msg_filter(17):
                print("[OK] Configurazione completata")
                return True
            else:
                print("[WARN] Impossibile configurare MSGFILTER")
                return True  # Continua comunque
        else:
            print(f"[ERROR] {self.client.last_error}")
            return False
    
    def print_weight(self, weight):
        """Stampa formattata pesata"""
        ts = datetime.now().strftime("%H:%M:%S")
        
        if self.show_json:
            print(json.dumps(weight.to_dict(), indent=2))
        else:
            print(f"\n{'='*70}")
            print(f"[PESATA] {ts} - #{len(self.weights)}")
            print(f"{'='*70}")
            print(f"  Timestamp:    {weight.timestamp}")
            print(f"  Batch:        '{weight.batch_code}'")
            print(f"  Recipe:       '{weight.recipe_name}'")
            print(f"  Line:         '{weight.line_code}'")
            print(f"  Serial:       {weight.serial_number}")
            print(f"  Peso:         {weight.weight_g:>8.3f} g  ({weight.weight_mg} mg)")
            print(f"  Delta:        {weight.delta_g:>+8.3f} g  ({weight.delta_mg:+d} mg)")
            print(f"  Class:        0x{weight.classification:05X}")
            print(f"  Flags:        {', '.join(weight.get_active_flags())}")
            
            # Status dettagliato
            status = []
            if weight.flag_expelled: status.append("ESPUlso")
            elif weight.flag_weight_ok: status.append("OK")
            elif weight.flag_weight_plus_plus: status.append("++")
            elif weight.flag_weight_plus: status.append("+")
            elif weight.flag_weight_minus_minus: status.append("--")
            elif weight.flag_weight_minus: status.append("-")
            
            if weight.flag_metal: status.append("METAL")
            
            print(f"  Status:       {' | '.join(status) if status else 'UNKNOWN'}")
        
        # Log su file
        if self.log_file:
            self.log_file.write(json.dumps(weight.to_dict()) + "\n")
            self.log_file.flush()
    
    def print_event(self, event):
        """Stampa formattata evento"""
        ts = datetime.now().strftime("%H:%M:%S")
        
        if self.show_json:
            print(json.dumps(event.to_dict(), indent=2))
        else:
            print(f"\n[! EVENTO] {ts}")
            print(f"  Codice:       {event.event_code} ({event.event_name})")
            print(f"  Descrizione:  {event.event_description}")
            print(f"  Batch:        '{event.batch_code}'")
            print(f"  Recipe:       '{event.recipe_name}'")
            print(f"  Operatore:    {event.operator}")
    
    def print_status(self, status):
        """Stampa formattata status"""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\n[STATSV] {ts}")
        print(f"  Code:         {status.status_code}")
        print(f"  Motor:        {status.motor_running.name}")
        print(f"  Work Mode:    {status.work_mode_enum.name}")
        print(f"  Production:   {'ON' if status.production_started else 'OFF'}")
        print(f"  Errors:       {'YES' if status.has_errors else 'NO'}")
        print(f"  Warnings:     {'YES' if status.has_warnings else 'NO'}")
    
    def print_stats(self):
        """Stampa statistiche sessione"""
        print(f"\n{'='*70}")
        print("STATISTICHE SESSIONE")
        print(f"{'='*70}")
        print(f"  Pesi ricevuti:    {self.client.stats['weights_received']}")
        print(f"  Eventi ricevuti:  {self.client.stats['events_received']}")
        print(f"  Comandi inviati:  {self.client.stats['commands_sent']}")
        print(f"  Errori:           {self.client.stats['errors']}")
        
        if self.weights:
            weights_g = [w.weight_g for w in self.weights]
            print(f"\n  PESI:")
            print(f"    Count:        {len(weights_g)}")
            print(f"    Media:        {sum(weights_g)/len(weights_g):.3f} g")
            print(f"    Min:          {min(weights_g):.3f} g")
            print(f"    Max:          {max(weights_g):.3f} g")
            print(f"    Range:        {max(weights_g) - min(weights_g):.3f} g")
    
    def process_message(self, msg: str):
        """Processa messaggio ricevuto"""
        if not msg:
            return
        
        # Parse WEIGHT
        if msg.startswith("WEIGHT="):
            weight = self.client.parse_weight(msg)
            if weight:
                self.weights.append(weight)
                self.print_weight(weight)
        
        # Parse EVENT
        elif msg.startswith("EVENT="):
            event = self.client.parse_event(msg)
            if event:
                self.events.append(event)
                self.print_event(event)
        
        # Parse STATSV (risposta a comando)
        elif msg.startswith("STATSV="):
            from idecon_client import IdeconStatus
            status = IdeconStatus()
            status.decode(msg[7:])
            self.print_status(status)
        
        # Parse STATP
        elif msg.startswith("STATP="):
            print(f"\n[STATP] Statistiche batch ricevute")
            self.client.stats['statp_received'] += 1
        
        # NEWPIECE
        elif "NEWPIECE" in msg:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] NEWPIECE - Differenza peso")
        
        # Altri
        elif msg.strip() and not msg.startswith("MSGFILTER"):
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {msg[:60]}")
    
    def run(self, duration: int = 0, poll_interval: int = 3):
        """
        Avvia monitor
        duration: 0 = infinito, altrimenti secondi
        poll_interval: intervallo polling STATSV in secondi
        """
        if not self.connect():
            return False
        
        self.running = True
        start_time = time.time()
        last_poll = 0
        
        print("\n" + "="*70)
        print("MONITOR AVVIATO")
        print("="*70)
        print(f"Modalità: {'JSON' if self.show_json else 'Human Readable'}")
        print(f"Durata: {'Infinita' if duration == 0 else f'{duration}s'}")
        print(f"Polling STATSV: ogni {poll_interval}s")
        print("\nPremi Ctrl+C per interrompere\n")
        
        try:
            while self.running:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Controlla durata
                if duration > 0 and elapsed >= duration:
                    print(f"\n[DURATA] Raggiunti {duration}s")
                    break
                
                # Polling STATSV
                if current_time - last_poll >= poll_interval:
                    try:
                        self.client.socket.sendall(b'\x02STATSV\x03')
                    except:
                        pass
                    last_poll = current_time
                
                # Ricezione dati
                ready = select.select([self.client.socket], [], [], 0.5)
                if ready[0]:
                    try:
                        data = self.client.socket.recv(1024)
                        if data:
                            # Rimuovi STX/ETX
                            if data[0] == 0x02:
                                data = data[1:]
                            if data[-1] == 0x03:
                                data = data[:-1]
                            
                            # Processa messaggio
                            msg = data.decode('ascii', errors='replace')
                            self.process_message(msg)
                    except:
                        pass
                
                # Mostra tempo rimanente
                if duration > 0:
                    remaining = duration - elapsed
                    print(f"\r  [{remaining:.0f}s rimanenti]", end="", flush=True)
                else:
                    print(f"\r  [In ascolto... {elapsed:.0f}s]", end="", flush=True)
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\n[INTERRUZIONE] Utente ha premuto Ctrl+C")
        
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Ferma monitor"""
        self.running = False
        self.print_stats()
        
        if self.log_file:
            self.log_file.close()
            print(f"\n[LOG] Salvato su file")
        
        self.client.disconnect()
        print("\n[DISCONNESSO]")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='IDECON Monitor CLI')
    parser.add_argument('--ip', default=IDEON_IP, help='IP bilancia')
    parser.add_argument('--port', type=int, default=IDEON_PORT, help='Porta')
    parser.add_argument('--duration', '-d', type=int, default=0, help='Durata in secondi (0=infinito)')
    parser.add_argument('--poll', '-p', type=int, default=3, help='Intervallo polling STATSV')
    parser.add_argument('--json', '-j', action='store_true', help='Output in formato JSON')
    parser.add_argument('--log', '-l', help='File di log (JSON Lines)')
    
    args = parser.parse_args()
    
    monitor = IdeconMonitorCLI(args.ip, args.port)
    monitor.show_json = args.json
    
    if args.log:
        monitor.log_file = open(args.log, 'w')
        print(f"[LOG] Aperto file: {args.log}")
    
    monitor.run(duration=args.duration, poll_interval=args.poll)


if __name__ == "__main__":
    main()