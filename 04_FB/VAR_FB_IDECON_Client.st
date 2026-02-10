VAR Internal
RxBuf	ARRAY[0..2047] OF BYTE			False	False	
RxLen	UINT			False	False	
i	UINT			False	False	
sTxCh	STRING[2]			False	False	
pos	INT			False	False	
modeCh	STRING[2]			False	False	
rxIdx	UINT			False	False	
readLen	UINT			False	False	
stxPos	INT			False	False	
etxPos	INT			False	False	
payloadLen	UINT			False	False	
tempStr	STRING[512]			False	False	
cmdQueue	STRING[255]			False	False	
cmdPending	BOOL			False	False	
prevEnable	BOOL			False	False	
prevCommandTrigger	BOOL			False	False	
VAR IN/OUT
Enable	Input	BOOL	No Edge		False	False	
MsgFilter	Input	UINT	No Edge		False	False	
RxIn	Input	ARRAY[0..511] OF BYTE	No Edge		False	False	
RxInLen	Input	UINT	No Edge		False	False	
RxInValid	Input	BOOL	No Edge		False	False	
TxConsumed	Input	BOOL	No Edge		False	False	
Command	Input	STRING[255]	No Edge		False	False	
CommandTrigger	Input	BOOL	No Edge		False	False	
LastSTATSV	Output	STRING[16]	No Edge		False	False	
WorkMode	Output	Idecon_WorkMode	No Edge		False	False	
Weight	Output	Idecon_WeightData	No Edge		False	False	
StatP	Output	Idecon_StatPData	No Edge		False	False	
LastMessage	Output	STRING[512]	No Edge		False	False	
HasMessage	Output	BOOL	No Edge		False	False	
TxOut	Output	ARRAY[0..511] OF BYTE	No Edge		False	False	
TxOutLen	Output	UINT	No Edge		False	False	
TxOutValid	Output	BOOL	No Edge		False	False	
Error	Output	BOOL	No Edge		False	False	
ErrorId	Output	UDINT	No Edge		False	False	
