/*
 * Test Connessione Bilancia IDECON (C#)
 * IP: 172.16.224.210 | Port: 50000
 * Protocollo: STX (0x02) + comando + ETX (0x03)
 */

using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;

namespace IdeconTest
{
    class Program
    {
        // Configurazione
        private const string IDEON_IP = "172.16.224.210";
        private const int IDEON_PORT = 50000;
        private const int TIMEOUT = 5000; // ms

        static void Main(string[] args)
        {
            Console.WriteLine("==================================================");
            Console.WriteLine("TEST CONNESSIONE BILANCIA IDECON (C#)");
            Console.WriteLine("==================================================");
            Console.WriteLine($"Target: {IDEON_IP}:{IDEON_PORT}");
            Console.WriteLine();

            bool useQuick = args.Length > 0 && args[0] == "--quick";

            if (useQuick)
            {
                QuickTest();
            }
            else
            {
                FullTest();
            }

            Console.WriteLine();
            Console.WriteLine("Test terminato. Premi un tasto per uscire...");
            Console.ReadKey();
        }

        static void FullTest()
        {
            using (TcpClient client = new TdpClient())
            {
                client.ReceiveTimeout = TIMEOUT;
                client.SendTimeout = TIMEOUT;

                try
                {
                    // 1. Connessione
                    Console.WriteLine("[1] Connessione in corso...");
                    client.Connect(IDEON_IP, IDEON_PORT);
                    Console.WriteLine("    OK - Connesso!");

                    NetworkStream stream = client.GetStream();

                    // 2. Invia STATSV
                    Console.WriteLine("[2] Invio comando STATSV...");
                    byte[] statsvCmd = CreateIdeconCommand("STATSV");
                    stream.Write(statsvCmd, 0, statsvCmd.Length);
                    Console.WriteLine($"    TX ({statsvCmd.Length} bytes): {ByteArrayToHex(statsvCmd)}");

                    // 3. Ricevi risposta STATSV
                    Console.WriteLine("[3] Attesa risposta STATSV...");
                    string response = ReadResponse(stream);
                    if (!string.IsNullOrEmpty(response))
                    {
                        Console.WriteLine($"    RX: {response}");
                    }
                    else
                    {
                        Console.WriteLine("    Nessuna risposta ricevuta");
                    }

                    // 4. Invia STATREQ
                    Console.WriteLine();
                    Console.WriteLine("[4] Invio comando STATREQ...");
                    byte[] statreqCmd = CreateIdeconCommand("STATREQ");
                    stream.Write(statreqCmd, 0, statreqCmd.Length);
                    Console.WriteLine($"    TX ({statreqCmd.Length} bytes): {ByteArrayToHex(statreqCmd)}");

                    // 5. Ricevi risposta STATP
                    Console.WriteLine("[5] Attesa risposta STATP...");
                    response = ReadResponse(stream);
                    if (!string.IsNullOrEmpty(response))
                    {
                        Console.WriteLine($"    RX: {response}");
                    }
                    else
                    {
                        Console.WriteLine("    Nessuna risposta ricevuta");
                    }

                    // 6. Test keep-alive (2 secondi)
                    Console.WriteLine();
                    Console.WriteLine("[6] Attesa 2s per eventuali pesate automatiche...");
                    Thread.Sleep(2000);

                    // Verifica dati pendenti
                    if (client.Available > 0)
                    {
                        byte[] extra = new byte[client.Available];
                        stream.Read(extra, 0, extra.Length);
                        Console.WriteLine($"    RX aggiuntivo: {ByteArrayToHex(extra)}");
                    }
                    else
                    {
                        Console.WriteLine("    Nessun dato aggiuntivo");
                    }

                    Console.WriteLine();
                    Console.WriteLine("==================================================");
                    Console.WriteLine("TEST COMPLETATO CON SUCCESSO!");
                    Console.WriteLine("==================================================");
                }
                catch (SocketException ex)
                {
                    Console.WriteLine();
                    Console.WriteLine($"ERRORE Socket [{ex.SocketErrorCode}]: {ex.Message}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine();
                    Console.WriteLine($"ERRORE: {ex.Message}");
                }
            }
        }

        static void QuickTest()
        {
            Console.WriteLine("QUICK TEST - Connessione semplice");
            Console.WriteLine(new string('-', 40));

            using (TcpClient client = new TdpClient())
            {
                client.ReceiveTimeout = TIMEOUT;

                try
                {
                    client.Connect(IDEON_IP, IDEON_PORT);
                    Console.WriteLine($"Connesso a {IDEON_IP}:{IDEON_PORT}");

                    NetworkStream stream = client.GetStream();

                    // Invia STATSV
                    byte[] cmd = CreateIdeconCommand("STATSV");
                    stream.Write(cmd, 0, cmd.Length);
                    Console.WriteLine($"Inviato: {ByteArrayToHex(cmd)}");

                    // Ricevi
                    Thread.Sleep(500);
                    if (client.Available > 0)
                    {
                        byte[] buffer = new byte[512];
                        int bytesRead = stream.Read(buffer, 0, buffer.Length);
                        byte[] response = new byte[bytesRead];
                        Array.Copy(buffer, response, bytesRead);
                        Console.WriteLine($"Ricevuto: {ByteArrayToHex(response)}");
                        Console.WriteLine($"Risposta: {ParseResponse(response)}");
                    }
                    else
                    {
                        Console.WriteLine("Nessuna risposta");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Errore: {ex.Message}");
                }
            }
        }

        static byte[] CreateIdeconCommand(string command)
        {
            // Protocollo: STX (0x02) + comando + ETX (0x03)
            byte[] cmdBytes = Encoding.ASCII.GetBytes(command);
            byte[] result = new byte[cmdBytes.Length + 2];

            result[0] = 0x02; // STX
            Array.Copy(cmdBytes, 0, result, 1, cmdBytes.Length);
            result[result.Length - 1] = 0x03; // ETX

            return result;
        }

        static string ReadResponse(NetworkStream stream)
        {
            byte[] buffer = new byte[512];
            int bytesRead = 0;

            // Leggi con timeout
            int attempts = 0;
            while (attempts < 20 && !stream.DataAvailable && bytesRead == 0)
            {
                Thread.Sleep(100);
                attempts++;
            }

            if (stream.DataAvailable)
            {
                using (MemoryStream ms = new MemoryStream())
                {
                    byte[] temp = new byte[512];
                    int read;

                    // Leggi tutti i dati disponibili
                    while (stream.DataAvailable && (read = stream.Read(temp, 0, temp.Length)) > 0)
                    {
                        ms.Write(temp, 0, read);
                    }

                    return ParseResponse(ms.ToArray());
                }
            }

            return string.Empty;
        }

        static string ParseResponse(byte[] data)
        {
            if (data == null || data.Length == 0)
                return string.Empty;

            // Rimuovi STX (0x02) e ETX (0x03)
            int start = 0;
            int end = data.Length;

            if (data.Length > 0 && data[0] == 0x02)
                start = 1;

            if (data.Length > start && data[data.Length - 1] == 0x03)
                end = data.Length - 1;

            int length = end - start;
            if (length <= 0)
                return string.Empty;

            byte[] payload = new byte[length];
            Array.Copy(data, start, payload, 0, length);

            return Encoding.ASCII.GetString(payload);
        }

        static string ByteArrayToHex(byte[] bytes)
        {
            return BitConverter.ToString(bytes).Replace("-", " ").ToUpper();
        }
    }
}