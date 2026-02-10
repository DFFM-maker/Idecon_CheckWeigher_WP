#!/usr/bin/env python3
"""
IDECON Web Dashboard - Flask + Socket.IO
Monitoraggio real-time via browser
"""

import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from idecon_client import IdeconClient, IDEON_IP, IDEON_PORT

app = Flask(__name__)
app.config['SECRET_KEY'] = 'idecon-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

class IdeconDashboard:
    """Backend dashboard con connessione IDECON"""
    
    def __init__(self, ip: str = IDEON_IP, port: int = IDEON_PORT):
        self.client = IdeconClient(ip, port)
        self.connected = False
        self.running = False
        self.weights = []
        self.events = []
        self.current_status = None
        self.max_weights_history = 100  # Mantieni ultimi 100 pesi
        
    def connect(self) -> bool:
        """Connessione alla bilancia"""
        if self.client.connect():
            self.connected = True
            self.client.set_msg_filter(17)
            return True
        return False
    
    def disconnect(self):
        """Disconnessione"""
        self.client.disconnect()
        self.connected = False
    
    def monitor_loop(self):
        """Loop di monitoraggio"""
        import select
        
        last_poll = 0
        
        while self.running and self.connected:
            try:
                current_time = time.time()
                
                # Polling STATSV ogni 3 secondi
                if current_time - last_poll >= 3:
                    try:
                        self.client.socket.sendall(b'\x02STATSV\x03')
                    except:
                        pass
                    last_poll = current_time
                
                # Ricezione dati
                ready = select.select([self.client.socket], [], [], 0.5)
                if ready[0]:
                    data = self.client.socket.recv(1024)
                    if data:
                        # Parse messaggio
                        if data[0] == 0x02:
                            data = data[1:]
                        if data[-1] == 0x03:
                            data = data[:-1]
                        
                        msg = data.decode('ascii', errors='replace')
                        self.process_message(msg)
                        
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(1)
    
    def process_message(self, msg: str):
        """Processa messaggio e invia a client web"""
        print(f"[DEBUG] Messaggio ricevuto: {msg[:60]}...")
        
        if msg.startswith("WEIGHT="):
            print(f"[DEBUG] Parsing WEIGHT...")
            weight = self.client.parse_weight(msg)
            if weight:
                print(f"[DEBUG] Peso parsato: {weight.weight_g:.3f}g - Flags: {weight.get_active_flags()}")
                # Aggiungi a storico
                self.weights.append({
                    'timestamp': datetime.now().isoformat(),
                    'weight_g': weight.weight_g,
                    'delta_g': weight.delta_g,
                    'batch_code': weight.batch_code,
                    'recipe_name': weight.recipe_name,
                    'flags': weight.get_active_flags()
                })
                
                # Mantieni solo ultimi N
                if len(self.weights) > self.max_weights_history:
                    self.weights = self.weights[-self.max_weights_history:]
                
                # Invia a tutti i client connessi
                socketio.emit('new_weight', {
                    'weight': weight.to_dict(),
                    'total_count': len(self.weights)
                })
                print(f"[DEBUG] WebSocket inviato! Total pesi: {len(self.weights)}")
        
        elif msg.startswith("EVENT="):
            event = self.client.parse_event(msg)
            if event:
                self.events.append({
                    'timestamp': datetime.now().isoformat(),
                    'event_code': event.event_code,
                    'event_name': event.event_name,
                    'description': event.event_description
                })
                
                socketio.emit('new_event', {
                    'event': event.to_dict()
                })
        
        elif msg.startswith("STATSV="):
            from idecon_client import IdeconStatus
            status = IdeconStatus()
            status.decode(msg[7:])
            self.current_status = status
            
            socketio.emit('status_update', {
                'status': status.to_dict()
            })
        
        elif "STATP=" in msg:
            socketio.emit('statistics_update', {
                'raw': msg[:100]
            })

# Istanza globale dashboard
dashboard = IdeconDashboard()

@app.route('/')
def index():
    """Homepage dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API: Stato connessione"""
    return jsonify({
        'connected': dashboard.connected,
        'stats': dashboard.client.stats,
        'weights_count': len(dashboard.weights),
        'events_count': len(dashboard.events)
    })

@app.route('/api/weights')
def api_weights():
    """API: Storico pesi"""
    return jsonify({
        'weights': dashboard.weights[-50:]  # Ultimi 50
    })

@app.route('/api/events')
def api_events():
    """API: Eventi"""
    return jsonify({
        'events': dashboard.events[-20:]  # Ultimi 20
    })

@socketio.on('connect')
def handle_connect():
    """Nuovo client connesso"""
    print(f"Client connesso: {request.sid}")
    
    # Invia stato attuale
    if dashboard.current_status:
        emit('status_update', {'status': dashboard.current_status.to_dict()})
    
    # Invia storico
    emit('weights_history', {'weights': dashboard.weights[-50:]})
    emit('events_history', {'events': dashboard.events[-20:]})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnesso"""
    print(f"Client disconnesso: {request.sid}")

@socketio.on('send_command')
def handle_command(data):
    """Ricezione comando da web"""
    cmd = data.get('command', '')
    if cmd and dashboard.connected:
        success, response = dashboard.client.send_command(cmd)
        emit('command_response', {
            'command': cmd,
            'success': success,
            'response': response
        })

def start_dashboard(ip: str = IDEON_IP, port: int = IDEON_PORT, 
                   web_port: int = 5000, debug: bool = False):
    """Avvia dashboard"""
    global dashboard
    
    print("="*70)
    print("IDECON WEB DASHBOARD")
    print("="*70)
    
    # Connessione bilancia
    dashboard = IdeconDashboard(ip, port)
    print(f"\nConnessione a {ip}:{port}...")
    
    if dashboard.connect():
        print("[OK] Connesso alla bilancia!")
        
        # Avvia thread monitor
        dashboard.running = True
        monitor_thread = threading.Thread(target=dashboard.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Avvia server web
        print(f"\n[WEB] Dashboard disponibile su:")
        print(f"  http://localhost:{web_port}")
        print(f"  http://127.0.0.1:{web_port}")
        print("\nPremi Ctrl+C per uscire\n")
        
        try:
            socketio.run(app, host='0.0.0.0', port=web_port, debug=debug)
        except KeyboardInterrupt:
            print("\n\nArresto in corso...")
        finally:
            dashboard.running = False
            dashboard.disconnect()
            print("[OK] Dashboard arrestata")
    else:
        print(f"[ERROR] Impossibile connettersi: {dashboard.client.last_error}")

if __name__ == "__main__":
    import argparse
    from flask import request
    
    parser = argparse.ArgumentParser(description='IDECON Web Dashboard')
    parser.add_argument('--ip', default=IDEON_IP, help='IP bilancia')
    parser.add_argument('--port', type=int, default=IDEON_PORT, help='Porta bilancia')
    parser.add_argument('--web-port', '-p', type=int, default=5000, help='Porta web server')
    parser.add_argument('--debug', action='store_true', help='Modalità debug Flask')
    
    args = parser.parse_args()
    
    start_dashboard(args.ip, args.port, args.web_port, args.debug)