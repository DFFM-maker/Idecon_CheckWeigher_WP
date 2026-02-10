#!/usr/bin/env python3
"""
IDECON Dashboard Debug - Test senza bilancia
"""

import json
import time
import random
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'idecon-debug'
socketio = SocketIO(app, cors_allowed_origins="*")

class FakeIdecon:
    """Simulatore bilancia per test"""
    
    def __init__(self):
        self.running = False
        self.weight_count = 0
        self.target_weight = 225.0  # g
        self.tolerance = 5.0
        
    def generate_weight(self):
        """Genera pesata fittizia realistica"""
        # Simula variazione casuale +/- 10g
        variation = random.uniform(-10, 10)
        weight_g = self.target_weight + variation
        delta_g = weight_g - self.target_weight
        
        # Determina classificazione
        classification = 0
        flags = []
        
        if abs(delta_g) <= 2:
            classification = 0x80  # OK
            flags = ["OK"]
            if delta_g > 0:
                classification |= 0x20000  # OK+
                flags = ["OK", "OK+"]
            elif delta_g < 0:
                classification |= 0x10000  # OK-
                flags = ["OK", "OK-"]
        elif delta_g > 5:
            classification = 0x10  # +
            flags = ["+"]
        elif delta_g > 10:
            classification = 0x8  # ++
            flags = ["++"]
        elif delta_g < -5:
            classification = 0x40  # -
            flags = ["-"]
        elif delta_g < -10:
            classification = 0x20  # --
            flags = ["--"]
        
        # 10% probabilità di essere espulso
        if random.random() < 0.1:
            classification |= 0x100  # EXPELLED
            if "EXPELLED" not in flags:
                flags.append("EXPELLED")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'production_order': 'ORD001',
            'batch_code': 'BATCH001',
            'recipe_name': '225g',
            'line_code': 'Linea1',
            'serial_number': 'ID02792',
            'weight_mg': int(weight_g * 1000),
            'weight_g': weight_g,
            'delta_mg': int(delta_g * 1000),
            'delta_g': delta_g,
            'classification': classification,
            'flags': flags
        }
    
    def simulate_loop(self):
        """Loop simulazione"""
        print("[DEBUG] Avvio simulazione pesate...")
        
        while self.running:
            # Ogni 2-5 secondi genera una pesata
            time.sleep(random.uniform(2, 5))
            
            if not self.running:
                break
            
            weight = self.generate_weight()
            self.weight_count += 1
            
            print(f"[DEBUG] Nuova pesata #{self.weight_count}: {weight['weight_g']:.3f}g")
            
            # Invia a tutti i client
            socketio.emit('new_weight', {
                'weight': weight,
                'total_count': self.weight_count
            })
            
            # Ogni 10 pesate, genera un evento
            if self.weight_count % 10 == 0:
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'event_code': 1004,
                    'event_name': 'BATCH_OPENING',
                    'event_description': 'Apertura nuovo lotto'
                }
                print(f"[DEBUG] Evento: {event['event_name']}")
                socketio.emit('new_event', {'event': event})

# Istanza simulatore
fake_idecon = FakeIdecon()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"[DEBUG] Client connesso")
    
    # Invia dati di test
    emit('status_update', {
        'status': {
            'status_code': '20110011',
            'motor_running': 'OPERATIONAL',
            'production_started': True,
            'has_errors': False,
            'work_mode': 'REMOTE'
        }
    })
    
    # Invia storico vuoto
    emit('weights_history', {'weights': []})
    emit('events_history', {'events': []})

@socketio.on('send_command')
def handle_command(data):
    print(f"[DEBUG] Comando ricevuto: {data}")
    emit('command_response', {
        'command': data.get('command'),
        'success': True,
        'response': 'OK (simulato)'
    })

def main():
    print("="*70)
    print("IDECON DASHBOARD - MODALITA DEBUG")
    print("="*70)
    print("\nQuesta modalità simula la bilancia per testare la dashboard")
    print("Le pesate vengono generate automaticamente ogni 2-5 secondi")
    print("\nAvvio server su http://localhost:5000")
    print("Premi Ctrl+C per uscire\n")
    
    # Avvia simulazione in thread separato
    fake_idecon.running = True
    sim_thread = threading.Thread(target=fake_idecon.simulate_loop)
    sim_thread.daemon = True
    sim_thread.start()
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nArresto...")
    finally:
        fake_idecon.running = False
        print("[OK] Server arrestato")

if __name__ == "__main__":
    main()