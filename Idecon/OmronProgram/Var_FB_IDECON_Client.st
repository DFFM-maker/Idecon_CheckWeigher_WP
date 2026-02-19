VAR IN/Out
Enable	Input	BOOL	No Edge		False	False	
Reset	Input	BOOL	No Edge		False	False	
Active	Output	BOOL	No Edge		False	False	
Error	Output	BOOL	No Edge		False	False	
ErrorID	Output	WORD	No Edge		False	False	

END_VAR

VAR INTERNAL
fbTcpConnect	SktTCPConnect			False	False	FB Connessione TCP
fbSocketRcv	SktTCPRcv			False	False	FB Ricezione socket
fbSocketSend	SktTCPSend			False	False	FB Invio socket
fbClose	SktClose			False	False	FB Chiusura socket
SocketHandle	_sSOCKET			False	False	Handle socket
bConnectDone	BOOL			False	False	Connessione completata
bConnectBusy	BOOL			False	False	Connessione in corso
bConnectError	BOOL			False	False	Errore connessione
wConnectErrorID	WORD			False	False	Codice errore connessione
bRcvDone	BOOL			False	False	Ricezione completata
bRcvBusy	BOOL			False	False	Ricezione in corso
bRcvError	BOOL			False	False	Errore ricezione
wRcvErrorID	WORD			False	False	Codice errore ricezione
bRcvExecute	BOOL	False		False	False	Execute FB ricezione
bNeedRcvRestart	BOOL	False		False	False	FIX#2: riavvio ricezione al prossimo scan
bSendDone	BOOL			False	False	Invio completato
bSendBusy	BOOL			False	False	Invio in corso
bSendError	BOOL			False	False	Errore invio
wSendErrorID	WORD			False	False	Codice errore invio
RxChunk	ARRAY[0..511] OF BYTE			False	False	Chunk dati ricevuti
RxChunkLen	UINT			False	False	Lunghezza chunk corrente
TxBuffer	ARRAY[0..511] OF BYTE			False	False	Buffer invio
RxBuf	ARRAY[0..2047] OF BYTE			False	False	Buffer accumulo frame
RxBufLen	UINT			False	False	Lunghezza buffer accumulato
tempBytes	ARRAY[0..511] OF BYTE			False	False	Temp per parsing payload
State	INT			False	False	State machine: 0=Connect 1=Online 99=Error
InitDone	BOOL			False	False	Inizializzazione socket completata
Connected	BOOL			False	False	Stato connessione attiva
CmdSent	BOOL			False	False	MSGFILTER=23 inviato con successo
SendActive	BOOL			False	False	Invio in corso
SendTimeout	UINT			False	False	Timeout invio (contatore scan)
i_Loop	INT			False	False	Contatore loop init socket
tonReconnect	TON			False	False	Timer riconnessione (10s)
tonWatchdog	TON			False	False	Watchdog assenza dati RX (60s)
stxPos	INT	-1		False	False	Posizione STX nel buffer
etxPos	INT	-1		False	False	Posizione ETX nel buffer
tempStr	STRING[512]			False	False	Stringa temp parsing
fieldStr	STRING[255]			False	False	Campo estratto dal parsing
pos	INT	0		False	False	Posizione find stringa
j	UINT			False	False	Indice generico
ix	UINT			False	False	Indice loop
payloadLen	UINT			False	False	Lunghezza payload frame corrente
idxShift	UINT			False	False	Indice shift buffer
classVal	UDINT			False	False	Valore bitmap classificazione
LastRxCount	UDINT			False	False	RxCount al ciclo precedente (watchdog)
RxTotalBytes	UDINT			False	False	Byte totali ricevuti
wf_weight_g	REAL			False	False	Peso corrente in grammi (Welford)
wf_delta	REAL			False	False	Delta Welford (old mean)
wf_delta2	REAL			False	False	Delta Welford (new mean)
wf_variance	REAL			False	False	Varianza corrente Welford
bResetPrev	BOOL	False		False	False	Edge detection Reset
Debug_LogIdx	UINT	0		False	False	Indice circolare log pesate
Debug_WeightLog	ARRAY[0..23] OF STRING[255]			False	False	Log ultime 24 pesate WEIGHT
Debug_Weights_classification	ARRAY[0..23] OF STRING[255]			False	False
classDW	DWORD			False	False	classVal castato a DWORD per AND bitwise (NJ)
charVal	BYTE			False	False
h_idx	INT			False	False	Indice loop hex
h_len	INT			False	False	Lunghezza stringa hex
h_char	BYTE			False	False	Carattere corrente
h_digit	UDINT			False	False	Valore numerico del carattere
Debug_State99Reason	UINT	0		False	False	Ultimo motivo State 99: 1=Watchdog 2=RcvError 3=ConnectError
Debug_State99ErrorID	WORD	0		False	False	Ultimo ErrorID che ha causato State 99
Debug_State99Count	UDINT	0		False	False	Contatore totale transizioni a State 99
Debug_WdogFireCount	UDINT	0		False	False	Contatore scatti watchdog 60s
Debug_RcvSoftErrCount	UDINT	0		False	False	Contatore errori benigni rx (0x0400 + 0x2006, non bloccanti)
END_VAR


VAR_EXTERNAL
IdeconInterface	False	
END_VAR
