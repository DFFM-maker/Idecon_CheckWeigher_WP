VAR Internal
tmpIpAddress	STRING[256]			False	False	
Config	_sSOCKET_ADDRESS	(PortNo := 50000, IpAdr := '172.16.224.200')		False	False	
tmpPort	UINT			False	False	
bConnectError	BOOL			False	False	
bEnableConnect	BOOL			False	False	
bConnectDone	BOOL			False	False	
bConnectBusy	BOOL			False	False	
wConnectErrorID	WORD			False	False	
bExecuteRcv	BOOL			False	False	
bRcvBusy	BOOL			False	False	
bRcvError	BOOL			False	False	
bRcvDone	BOOL			False	False	
fbSocketRcv	SktTCPRcv			False	False	
RxChunk	ARRAY[0..511] OF BYTE			False	False	
wRcvErrorID	WORD			False	False	
rTrigValid	R_TRIG			False	False	
sCurrentRecipe	STRING[64]			False	False	
tonTestTimeout	TON			False	False	
pollResetSV	BOOL			False	False	
pollResetP	BOOL			False	False	
tonPollingSTATSV	TON			False	False	
tonPollingSTATP	TON			False	False	
prevPollSVQ	BOOL			False	False	
prevPollPQ	BOOL			False	False	
Idecon	FB_IDECON_Client			False	False	
MsgFilter	UINT	17		False	False	
newMsg	BOOL			False	False	
prevLastMessage	STRING[512]			False	False	
sTempParse	STRING[255]			False	False	
newWeightMsg	BOOL			False	False	
prevWeightMsg	BOOL			False	False	
tmpWeightData	Idecon_WeightData			False	False	
tmpStatPData	Idecon_StatPData			False	False	
bSendError	BOOL			False	False	
totalRejected	DINT			False	False	
sendTrigger	BOOL			False	False	
prevTxOutValid	BOOL			False	False	
TxBuffer	ARRAY[0..511] OF BYTE			False	False	
fbSocketSend	SktTCPSend			False	False	
bSendDone	BOOL			False	False	
bSendBusy	BOOL			False	False	
wSendErrorID	WORD			False	False	
END_VAR


VAR External
HMI_MachineSetUp	False	
HMI_OnLineData	False	
FLAG	False	
HMI_OnlineStatistics	False	
SEQUENCE	False	
HMI_NoRecipeMachine	False	
AXIS	False	
ScadaInterface	False	
MachineAnalytics	False	
HMI_RecipeMachine	False	
HMI_RecipeName	False	
D_Recipes	False	
RecipeArchives	False	
TimeZoneAndDLS_DateTime	False	
ScadaLogs	False	
G_Idecon_HMI_Cmd	False	
G_Test_Ejector_Start	False	
G_Test_Ejector_Restore	False	
G_Idecon_LastWeight	False	
G_Idecon_StatP	False	
G_Test_Ejector_State	False	
G_Test_Saved_Offset	False	
G_Test_Saved_Duration	False	
G_ProgressiveID	False	
G_Idecon_LastSTATSV	False	
G_System_Error	False	
G_OPCUA_Idecon	False	
G_Idecon_WorkMode	False	
G_Idecon_BatchCode	False	
G_Idecon_ProductionOrder	False	
   
.