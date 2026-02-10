
# Weighers remote connection manual

Version 2.7
Date 11/05/2023

IDECON s.r.l.
via dell'Industria, 242
48014 Castel Bolognese (RA)
Italia

VAT Code: 02214260396
telephone: +39 0546 50083
fax: +39 0546 655328

www.idecon.it
e-mail: info@idecon.it

## WEIGHERS REMOTE CONNECTION MANUAL

### 1 INTRODUCTION
1.1 GENERAL SYNTAX
1.2 INFORMATION SENT AUTONOMOUSLY BY THE WEIGHER

### 2 COMMANDS
2.1 START
2.2 STOP
2.3 RECIPE
2.4 STATSV
2.5 ERRNUM
2.6 BATCHSTART
2.7 BATCHSTOP
2.8 SHUTDOWN
2.9 LINECODE
2.10 RESETERRORI
2.11 ENABLESTATS
2.12 STATCADENCY
2.13 DISABLESTATS
2.14 SELSTATSANSWER
2.15 STATREQ
2.16 STATREQATB
2.17 INFORECIPE
2.18 GETRECIPELIST
2.19 BATCHMODIFY
2.20 BATCHINFO
2.21 MSGFILTER
2.22 ENABLESTARTBUTTON
2.23 SHOWMESSAGE
2.24 DATETIME
2.25 MODIFICATION OF THE RECIPE WITH ALTERRECIPE
2.26 RECIPE PARAMETER IDENTIFIERS.
  2.26.1 TARE.
  2.26.2 WEIGHT.
  2.26.3 PRODUCT_CODE
  2.26.4 LIMITS_VALUE.
  2.26.5 LIMIT_TYPE
  2.26.6 THROUGHPUT.
  2.26.7 LENGTH
  2.26.8 DEBOUNCING_FILTER
  2.26.9 EJECTOR_1, EJECTOR_2, EJECTOR_3, EJECTOR_4.
  2.26.10 MAXIMUM_CONSECUTIVE_EJECTION.
  2.26.11 PERCENTAGE_OF_PRODUCT_M_TO_ACCEPT.
  2.26.12 FBK_ENABLE...
  2.26.13 FBK_TARGET_WEIGHT_ADJUSTER.
  2.26.14 FBK_PIECES_TO_AVERAGE
  2.26.15 FBK_PIECES_TO_WAIT...
  2.26.16 FBK_NO_CORRECTION_THRESHOLD
  2.26.17 FBK_K_FACTOR
  2.26.18 FBK_MAXIMUM_CORRECTION
  2.26.19 FBK_STANDBY_TIME.
  2.26.20 FBK_STANDBY_PIECES
  2.26.21 FBK_NON_OPERATION_THRESHOLD...
  2.26.22 OPTION_A..
  2.26.23 OPTION_B
  2.26.24 MOTOR_4_SPEED_PERCENTAGE_COMPARED_MOTOR_2
  2.26.25 SCREWFEEDER_PTC_IN_OUT_TIMEOUT
  2.26.26 METAL_SENSITIVITY.
  2.26.27 METAL_PHASE
  2.26.28 METAL_FREQUENCY
  2.26.29 METAL_ANALISYS_MODE
  2.26.30 METAL_REVELATION_MODE
  2.26.31 METAL_Z..
  2.26.32 METAL_TESTER_DIAMETERS
  2.26.33 SPEED_CONVEYOR_BELT_1
  2.26.34 SPEED_CONVEYOR_BELT_2
  2.26.35 SPEED_CONVEYOR_BELT_3
  2.26.36 MOTOR_STOP_DELAY_ON_EXIT_PTC..
  2.26.37 USRCNT_RESET_VALUE....
  2.26.38 USRCNT_ON_EXPIRATION_ACTION.
  2.26.39 USRCNT_ACTION_RESET...
  2.26.40 USRCNT_OUTPUT_ACTIVATION_TIME
  2.26.41 USRCNT_NOTIFICATION_ACTIVATION_TIME.
  2.26.42 EXISTS.
  2.26.43 NEW
  2.26.44 DELETE
2.27 CONSULT A RECIPE WITH GETFROMRECIPE
2.28 GET_CURRENT_PIECE_STAT.
2.29 PIECE_STAT
2.30 STATUS
2.31 BATCHCHANGE

### 3 NOTIFICATIONS SENT BY THE WEIGHER
3.1 EVENTS
  3.1.1 EVENT.
3.2 STATISTICS
  3.2.1 STATP
  3.2.2 STATPATB.
3.3 RECIPE DATA:
  3.3.1 INFORECIPE
3.4 WEIGHINGS:
  3.4.1 Individual weighing WEIGHT.
3.5 BATCHES AND PRODUCTION
  3.5.1 Information of the BATCHINFO batch.
  3.5.2 EndOfBatch batch closing notification...
3.6 DATE AND TIME
  3.6.1 Actual date and time DATETIME

### 4 EXAMPLE OF COMMUNICATION
4.1 EXAMPLE OF WEIGHTS AND STATISTICS SENDING..
4.2 EXAMPLE OF PRODUCTION CHANGE

### 5 INDEX OF THE TABLES

### 6 INDEX OF THE COMMANDS AND NOTIFICATIONS..

---

## 1 Introduction

The IDECON weighers envision a two-way communication channel via TCP/IP socket, through which it is possible to send commands and receive information.
The configuration channel must be activated and configured before being used.
On start-up, the weigher prepares itself in server mode and accepts just one connected client.
The port used by the weigher for the connection can be configured.
The weigher normally behaves as a server and accepts and responds to commands received.
In some conditions, it is possible that the weigher autonomously sends information on the communication channel. For a complete list of the notifications sent, see **Information sent autonomously by the weigher**.
The weigher responds to every command received; it responds with the command itself to indicate that the command has been implemented.
STATCADENCY=60 (sent command)
STATCADENCY (answer)

Some commands envision an immediate response:
STATSV=60 (sent command)
STATSV=01000011 (answer)

### 1.1 General syntax

Every message towards the weigher (command) or message from the weigher (notification) is sent with a precise syntax and the upper and lower case characters must be respected.
Every message must be embedded between two delimiters called <STX> and <ETX>.

<STX> delimits the start of the message, it is made up from the ASCII hexadecimal 0x02 character.
<ETX> delimits the end of the message, it is made up from the ASCII hexadecimal 0x03 character.

The message will be altogether composed by three strings: <STX>, the command/notification and <ETX>. The two delimiters are not the character "2" and "3", since that their hexadecimal ASCII representations differ from the desired ones. Equivalently the delimiters can be defined through binary representation of numbers 2 and 3.

Figure 1: Communication example (Conceptual diagram of STX, command/notification, ETX)

Syntax:
\`\`\`
<STX>MESSAGE<ETX>
<STX>MESSAGE=Value<ETX>
<STX>MESSAGE=Value 1 Value 2|| Value n|<ETX>
\`\`\`
Some messages may envision additional data, the message is separated from the data by the = character (ASCII hexadecimal 0x3D).
The data contained in the message are separated from each other by the | character (ASCII hexadecimal 0x7C).

### 1.2 Information sent autonomously by the weigher

The weigher can send information to the client in the following conditions:
*   **WEIGHT** - individual weighing, see **WEIGHT** section.
*   **EVENT** - event or error, see **EVENT** section.
*   **STATP** - production statistics, see **STATP** section.
*   **STATPATB** - production statistics, see **STATPATB** section.
*   **EndOfBatch** - Batch end statistics, see **EndOfBatch batch closing notification** section.

## 2 Commands

The commands sent to the weigher must respect the precise syntax; the upper and lower case letters must be respected.
The weigher responds to every command recognized with the command itself.
Some commands envision the presence of additional data in the response; consult the description of the individual commands.
The remote connection is supported on the weigher versions which mount 12" and 7" monitors. However, the functionalities in the 7" weigher versions are limited respect to the 12" weigher versions. For this reason, it could be possible that some commands described in this manual are not supported. For each command, it is specified which monitor models support such command, any difference in terms of notation or returned messages. If the user executes a non-supported command on a 7" devices, the latter will return an ERRCMD command.

### 2.1 START

**Supported on devices:** 12", 7"
Starts the weigher in weighing mode.

**ATTENTION!!** To use this command, the weigher must be appropriately protected from the entry of operators, since the belts are made to move.
The weigher will be operational (STARTED status) at the end of the conveyors motors adjustment phase.
Remember that it is not possible to start the checkweigher with such command in local mode. To know if the checkweigher works in local mode, refer to **Detailed machine status table**.

**Syntax:**
\`\`\`
START
\`\`\`

**Response 12":**
\`\`\`
START
\`\`\`
if the command has been accepted.
\`\`\`
START [error]
\`\`\`
if the command has not been accepted, the cause is contained in the response (instead of [errore]).

**Response 7":**
\`\`\`
START
\`\`\`
if the command has been accepted.
\`\`\`
ERRCMD
\`\`\`
if the command has not been accepted. No further information is sent.

### 2.2 STOP

**Supported on devices:** 12", 7"
Stops the weighing mode of the weigher; the belts stop.

**Syntax:**
\`\`\`
STOP
\`\`\`

**Response:**
\`\`\`
STOP
\`\`\`
if the command has been accepted.

### 2.3 RECIPE

**Supported on devices:** 12", 7" (if the recipe does not exist, Dummy recipe will be automatically selected)
Selects the working recipe if indicated below or requires the currently selected recipe. At switch on the machine selects the last recipe opened by default (if it is not found, an error is signaled). A recipe can only be selected with the machine at a standstill (STOPPED status).

**Syntax:**
1) \`RECIPE\`
2) \`RECIPE=[recipe name]\`

**Response 12":**
1) \`RECIPE=Product100g\`
command accepted, the recipe goes back to active.
2) \`RECIPE\`
command accepted, if the recipe does not exist another error message is sent:
\`\`\`
EVENT-2018/27/6 2:10:21 PM production
order||Product100g|LineaTest_1|ID00000|Cod. 4352|Errore: Apertura ultimo
programma fallita: [recipe name] non trovato!|supervisor|
\`\`\`

**Response 7":**
1) \`RECIPE=Product100g\`
command accepted, the recipe goes back to active.
2) \`RECIPE\`
command accepted. If the recipe does not exist, no error message is returned, but the Dummy recipe will be automatically selected.

### 2.4 STATSV

**Supported on devices:** 12", 7"
Requires the status of the weigher. The states are coded using a series of values.
Every value represents a weigher status; the meaning of the position is described in **Detailed machine status table**.

**Syntax:**
\`\`\`
STATSV
\`\`\`

**Response:**
\`\`\`
STATSV-00000011
\`\`\`
From this example it can be seen that the weigher is at a standstill, there are no errors, the batch is closed and the interface is in LOCAL mode.

**Detailed machine status table**

| Position | Description of the Detailed Machine Status                                                                        |
| :------- | :---------------------------------------------------------------------------------------------------------------- |
| 1        | Status of the checkweigher (0=standstill, 1=adjustment in progress, 2=ready to weigh, 3=energy saving, 4=recovery from energy saving) |
| 2        | Production started flag (1=yes)                                                                                   |
| 3        | Presence of errors (1=yes)                                                                                        |
| 4        | Presence of warning (1=yes)                                                                                       |
| 5        | Presence of messages (1=yes)                                                                                      |
| 6        | The statistics sending in enabled (1=yes, the sending frequency is specified via STATCADENCY)                     |
| 7        | Checkweigher work mode (1=local, 2=remote, 3=maintenance)                                                         |
| 8        | Status of the connection                                                                                          |

### 2.5 ERRNUM

**Supported on devices:** 12", 7"
Returns the last flagged error type on the interface. If there are no errors, it will return the value zero.

**Syntax:**
\`\`\`
ERRNUM
\`\`\`

**Response:**
\`\`\`
ERRNUM=0
\`\`\`
command accepted, it returns the last flagged error type.

### 2.6 BATCHSTART

**Supported on devices:** 12", 7"
Starts the production of a new batch.

**Syntax:**
\`\`\`
BATCHSTART
\`\`\`

**Response:**
\`\`\`
BATCHSTART
EVENT=2018.06.27 13:55:50|production order|batch
code|recipe|LineaTest_1|ID00000|Cod. 1004|Evento: Apertura Lotto||
\`\`\`
It is recommended to verify always if the batch has been opened through the **STATSV** command (refer to the **Detailed machine status table**). Remember that, in 12" devices, if the user tries to open a batch with a previously open batch, an error message will be visualized.

**Response 12":**
\`\`\`
EVENT-2021/19/3 11:00:57 AM|5678|1234|Dummy|codlin|ID 00000|Cod. 0000|Errore:
Comando remoto di apertura lotto con lotto gia aperto, chiudere prima lotto
corrente|supervisor|
\`\`\`
In 7" devices, the next BATCHSTART will be simply ignored.

### 2.7 BATCHSTOP

**Supported on devices:** 12", 7"
Closes the production of the open batch.

**Syntax:**
\`\`\`
BATCHSTOP
\`\`\`

**Response:**
\`\`\`
EVENT-2021.03.19 10:49:32|5678|1234|Dummy|codlin|ID 00000|Cod. 0000|Evento:
Chiusura Lotto|supervisor|
BATCHSTOP
\`\`\`
It is recommended to verify always if the batch has been closed through the **STATSV** command (refer to the **Detailed machine status table**). Remember that, in 12" devices, if the user tries to close a batch with the already closed batch, an error message will be visualized.

**Response 12":**
\`\`\`
EVENT-2021/19/3 11:04:38 AM|5678||Dummy|codlin|ID 00000|Cod. 0000|Errore:
Operazione di apertura/chiusura lotto fallita|supervisor|
\`\`\`
In 7" devices, the next BATCHSTOP will be simply ignored.

### 2.8 SHUTDOWN

**Supported on devices:** 12"
Sends a weigher switch-off request.

**Syntax:**
\`\`\`
SHUTDOWN
\`\`\`

**Response:**
\`\`\`
SHUTDOWN
\`\`\`

### 2.9 LINECODE

**Supported on devices:** 12", 7"
Requires the code of the line associated to the weigher.

**Syntax:**
\`\`\`
LINECODE
\`\`\`

**Response:**
\`\`\`
LINECODE=LineaTest_1
\`\`\`

### 2.10 RESETERRORI

**Supported on devices:** 12", 7"
Cancels the weigher errors visible in the associated interface window.

**Syntax:**
\`\`\`
RESETERRORI
\`\`\`

**Response:**
\`\`\`
RESETERRORI
\`\`\`

### 2.11 ENABLESTATS

**Supported on devices:** 12", 7"
Activates the automatic sending of the statistics by the checkweigher. The message used for the statistics depends on the selection done through the command **SELSTATSANSWER**.
To change the frequency with which the statistics are sent, use the **STATCADENCY** command.

**Syntax:**
\`\`\`
ENABLESTATS
\`\`\`

**Response:**
\`\`\`
ENABLESTATS
\`\`\`

### 2.12 STATCADENCY

**Supported on devices:** 12", 7"
Modifies the frequency, expressed in seconds, with which the weigher sends the statistics to the client.
This command modifies only the frequency; it can be sent at any time.
To activate statistics sending, use the **ENABLESTATS** command.

**Syntax:**
\`\`\`
STATCADENCY=[seconds]
\`\`\`

**Response:**
\`\`\`
STATCADENCY
\`\`\`

### 2.13 DISABLESTATS

**Supported on devices:** 12", 7"
Deactivates the automatic sending of the statistics by the checkweigher.

**Syntax:**
\`\`\`
DISABLESTATS
\`\`\`

**Response:**
\`\`\`
DISABLESTATS
\`\`\`

### 2.14 SELSTATSANSWER

**Supported on devices:** 12", 7"
Select which message will be used for the automatic notification of the production statistic by the checkweigher.
The statistic is sent automatically if the **ENABLESTATS** command is activated or at batch closing.
The command returns always the last valid selection. In case of a command with a wrong parameter, it selects the STATP choice.

**Syntax:**
\`\`\`
SELSTATSANSWER
SELSTATSANSWER=[STR value]
\`\`\`

**Allowed value:**
STATP, STATPATB

**Response:**
\`\`\`
SELSTATSANSWER=[STR value]
\`\`\`

### 2.15 STATREQ

**Supported on devices:** 12", 7"
Requests the weigher to send the current production statistics via the STATP message.
This command can be sent at any time.

**Syntax:**
\`\`\`
STATREQ
\`\`\`

**Response:**
\`\`\`
STATREQ
\`\`\`
command accepted, the **STATP** notification will be sent with the data of the statistics updated at the time of the request.

### 2.16 STATREQATB

**Supported on devices:** 12", 7"
Requests the weigher to send the current production statistics via the STATPATB message.
This command can be sent at any time.

**Syntax:**
\`\`\`
STATREQATB
\`\`\`

**Response:**
\`\`\`
STATREQATB
\`\`\`
command accepted, the **STATPATB** notification will be sent with the data of the statistics updated at the time of the request.

### 2.17 INFORECIPE

**Supported on devices:** 12", 7"
Requests to the weigher the information relative to the current recipe.

**Syntax:**
\`\`\`
INFORECIPE
\`\`\`

**Response:**
\`\`\`
INFORECIPE=[recipe]|prod.code=[product code]|weight=[nominal
weight]|tare=[nominal tare]|lim-=[limit -]|lim+=[limit +]|lim--=[limit
--]|lim++=[limit ++]|
\`\`\`

**Example:**
\`\`\`
INFORECIPE=Product100g|prod.code=product_code|weight=100.0|tare=1.2|lim-
=95.5|lim+=104.5|lim--=91.0|lim++=109.0|
\`\`\`

### 2.18 GETRECIPELIST

**Supported on devices:** 12"
Request to the weigher the recipes list.
The command reply implies the sending of a bunch of information, or a series of data which respect the following sequence:
*   Reply to the command with sequence identifier (it would be different every time)
*   Start of data sequence notification
*   Data; every recipe name would be sent separately
*   End data sequence notification

**Attention!!** The checkweigher can send on the socket channel even other information which are non-coherent to the GETRECIPELIST command before the data sequence ending notification.
Sequence identifier is incremental and at each checkweigher restart it would be automatically reset. When the identifier reaches 99, the counter continues (DS100, DS 101, ecc).

**Syntax:**
\`\`\`
GETRECIPELIST
\`\`\`

**Response:**
\`\`\`
GETRECIPELIST=ACCEPTED|DS[sequence identificator Unsigned INT]
\`\`\`

**Notification of the begin data sequence:**
\`\`\`
DS [sequence identificator Unsigned INT]=BEGIN
\`\`\`

**Data:**
\`\`\`
DS [sequence identificator Unsigned INT]=[recipe name]
\`\`\`

**Notification of the end data sequence:**
\`\`\`
DS [sequence identificator Unsigned INT]=END
\`\`\`

**Example of a single sequence (A single GETRECIPELIST request):**
\`\`\`
GETRECIPELIST=ACCEPTED|DS05
DS05-BEGIN
DS05=250g
DS05=500g
DS05=1000g
DS05-END
\`\`\`

**Example of a double sequence (Two consecutives GETRECIPELIST commands):**
\`\`\`
GETRECIPELIST=ACCEPTED|DS07
DS07-BEGIN
DS07=250g
GETRECIPELIST=ACCEPTED|DS08
DS07=500g
DS08-BEGIN
DS08=250g
DS08=500g
DS07=1000g
DS08=1000g
DS07-END
DS08-END
\`\`\`

### 2.19 BATCHMODIFY

**Supported on devices:** 12", 7"
This command allows to modify some batch parameters individually before the batch is opened.
This command can be used only if the checkweigher interface is on the main page or if it is in remote mode, the batch must be closed.
If the command is not accepted, "REFUSED" is added in the response.

**Batch data identifiers table**

| Batch data identifier | Meaning          |
| :-------------------- | :--------------- |
| OPERATOR            | Operator         |
| BATCHCODE           | Batch code       |
| PRODUCTIONORDER     | Production order |
| EXTRAFIELD1         | Extra 1 field    |
| EXTRAFIELD2         | Extra 2 field    |

**Syntax:**
\`\`\`
BATCHMODIFY=[OPERATOR,BATCHCODE, PRODUCTIONORDER,EXTRAFIELD1,EXTRAFIELD2]|[valore]
\`\`\`

**Response:**
\`\`\`
BATCHMODIFY
\`\`\`
\`\`\`
BATCHMODIFY REFUSED
\`\`\`

**Command examples with relative response:**
\`\`\`
BATCHMODIFY=BATCHCODE|BATCH12345
BATCHMODIFY
\`\`\`

### 2.20 BATCHINFO

**Supported on devices:** 12", 7"
This command allows the batch parameters to be requested.
The returned data from the command are the ones contained in the weigher batches modification page. It is possible to use this command even if the batch has not been opened.
To interpret the data, refer to **Information of the BATCHINFO batch** section.

**Syntax:**
\`\`\`
BATCHINFO
\`\`\`

**Response:**
\`\`\`
BATCHINFO=%s%s%s%s%s%s%s%s%ld %s%ld|%s%d:%d|%s|
\`\`\`

**Example:**
**Response 12":**
\`\`\`
BATCHINFO=supervisor|5000|7530|||SPLIT|GLOBAL|PIECES|6|PIECES|1|DISABLED|0:0|
MANUAL|
\`\`\`

**Response 7":**
\`\`\`
BATCHINFO=Lotto Attivo|5200|1234|||GLOBAL|GLOBAL|MANUAL| |NOT
SELECTED||DISABLED|||
\`\`\`

**BATCHINFO parameters table**

| Field | Description                                                                                             |
| :---- | :------------------------------------------------------------------------------------------------------ |
| %s    | Name of the operator                                                                                    |
| %s    | Production code                                                                                         |
| %s    | Production order                                                                                        |
| %s    | Extra 1 field                                                                                           |
| %s    | Extra 2 field                                                                                           |
| %s    | Batch type (GLOBAL, SPLIT)                                                                              |
| %s    | Community legislation (NOT_SELECTED, GLOBAL, SPLIT, DISABLED)                                           |
| %s    | Type of production end (NOT_SELECTED, PIECES, MINUTES, MANUAL)                                          |
| %ld   | Value associated to the type of production end, specifies a number of pieces or a time.                 |
| %s    | Type of split batch end (NOT_SELECTED, PIECES, MINUTES)                                                 |
| %s    | Value associated to the type of split batch end, specifies a number of pieces or a time.                 |
| %s    | Open-close batch option by time (ENABLED, DISABLED)                                                     |
| %s    | Batch opening-closing time in hh:mm format                                                              |
| %s    | Overall batch print option (MANUAL, AUTOMATIC)                                                          |

### 2.21 MSGFILTER

**Supported on devices:** 12", 7"
This command allows to select which type of information is sent by the weigher.
The command can be sent to the weigher without MSGFILTER value to request the current value or associated to the new filter value MSGFILTER=63.
The response always contains current filter value.
The filter is an integer value interpreted with a bit mask; the values that can be used are described in the **Mask for filter of the messages sent by the weigher** table.
It is possible to enable one or more messages by combining the various bits in OR, e.g. responses+individual weighings via the value 17 (bit0=1 OR bit4=17)

**Syntax:**
\`\`\`
MSGFILTER=[valore]
\`\`\`

**Response:**
\`\`\`
MSGFILTER=[valore]
\`\`\`

**Command examples with relative response:**
\`\`\`
MSGFILTER
MSGFILTER=63
\`\`\`

**Mask for filter of the messages sent by the weigher**

| Bit | Description                                                                                                                                                                                            |
| :-- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0   | **Responses only.** The weigher sends the command just received, only if the command has been recognized. The weigher sends the response to the received command. The commands, which envision an immediate response are: LINECODE, STATUS, STATSV, ERRNUM, STATREQ, STATREQATB, INFORECIPE, MSGFILTER. |
| 1   | **Errors.** The weigher sends the list of the currently present errors and the errors zeroing event.                                                                                                   |
| 2   | **Events.** The weigher sends all checkweigher events as for example recipe change, batch start-finish, modified machine parameters....                                                                    |
| 3   | **Statistics.** If enabled, the weigher sends the statistics information to the timer with ENABLESTATS.                                                                                                  |
| 4   | **Individual weights.** The weigher sends all the performed weighings.                                                                                                                                 |
| 5   | **Important messages.** The weigher sends important messages; currently SHUTDOWN lies within such category.                                                                                             |

### 2.22 ENABLESTARTBUTTON

**Supported on devices:** 12"
This command allows to enable or disable the start button present in the weigher interface.
This command can be used only with the checkweigher in remote mode.
The command can be used with or without parameters; in the former case it sets the start button current status, while in the latter case it returns the current status of the same button.
If the 0 value is specified, the button is disabled; if the value is one, the button is activated.

**Syntax:**
\`\`\`
ENABLESTARTBUTTON
ENABLESTARTBUTTON=[0,1]
\`\`\`

**Response:**
\`\`\`
ENABLESTARTBUTTON=[0,1]
\`\`\`

### 2.23 SHOWMESSAGE

**Supported on devices:** 12"
This command allows to visualize a message on the checkweigher display. The message occupies the entire screen and makes the weigher interface temporarily unusable.
If no character is specified after the = character, the message box is removed.

**Syntax:**
\`\`\`
SHOWMESSAGE=
SHOWMESSAGE=[message]
\`\`\`

**Response:**
\`\`\`
SHOWMESSAGE
\`\`\`

### 2.24 DATETIME

**Supported on devices:** 12", 7"
This command allows to modify or request the date and the time of the weigher.
The command without parameters requests the current date and time from the checkweigher; for the response see **DATETIME** section.
The command with parameters allows to modify the weigher date and time; the number of seconds is optional.
If the command is not accepted, REFUSED is added in the response, followed by the error that has generated refusal.

**Syntax:**
\`\`\`
DATETIME=%2d/%2d/%4d|%2d:%2d:%2d.%3d|
DATETIME=[dd/mm/yyyy|hh:mm:ss]
DATETIME=[dd/mm/yyyy|hh:mm]
DATETIME
\`\`\`

**Response:**
\`\`\`
DATETIME=[dd/mm/yyyy|hh:mm:ss.msec]
\`\`\`
For additional information, see **DATETIME** section.
\`\`\`
DATETIME=REFUSED|[descrizione del motivo che non consente questa operazione]
\`\`\`

**Example of response for incorrect syntax:**
\`\`\`
DATETIME=REFUSED| use DATETIME =dd/mm/yyyy|hh:mm:ss.msec] ([:ss.msec] is
optional)
\`\`\`

**Example of response for date and time that are non-modifiable or non-acceptable:**
\`\`\`
DATETIME=REFUSED| Nel sistema è stata rilevata una data più recente di quella
inserita. Data del lotto più recente: 28/06/2018-09:07:07.113 RICETTA:
Prodotto100g Inserire data ed ora corretti
\`\`\`

**Table of DATETIME parameters**

| Field | Description                    |
| :---- | :----------------------------- |
| %2d   | Number of the day in 2 digits  |
| %2d   | Number of the month in 2 digits |
| %4d   | Number of the year in 4 digits |
| %2d   | Hours in 24h format            |
| %2d   | Number of the minutes in 2 digits |
| %2d   | Number of the seconds in 2 digits |
| %3d   | Number of the milliseconds in 3 digits |

**Note.**
The fields that specify the number of digits (%2d, %3d, %4d) must always contain all the required digits. If the number to represent is made up from less digits than those required, place Os in front of the number until the number of digits required is reached.

**Table of examples of formatting of numerical values**

| Original value | %2d           | %3d           | %4d           |
| :------------- | :------------ | :------------ | :------------ |
| 4              | 04            | 004           | 0004          |
| 25             | 25            | 025           | 0025          |
| 280            | Non-representable | 280           | 0280          |

### 2.25 Modification of the recipe with ALTERRECIPE

**Supported on devices:** 12"
This command allows to modify individual data of the recipes contained in the weigher.
Modify the parameters of a recipe, may make it unusable.
The modification takes place via the ALTERRECIPE command followed by the recipe name, the identifier of the data to be modified and, with the exception of some commands, from the new data.
As a response, the command returns, ALTERRECIPE=ACCEPTED if the modification command has been successful.
As a response, the command returns, ALTERRECIPE=REFUSED| numerical code:error description parameters of the code that has generated the error if the command has been received but it was not possible to modify the data.
Some identifiers can return an error description even if the command has been accepted (ALTERRECIPE=ACCEPTED|code:error description); for further information refer to the individual identifiers of the parameters.
Some identifiers are only present in some types of weigher.
There can be various types of error:

**Table of the types of ALTERRECIPE command errors**

| Type of error     | Description                                                                                               |
| :---------------- | :-------------------------------------------------------------------------------------------------------- |
| Syntax error      | The command is not formatted correctly.                                                                   |
| Invalid value     | The specific value is not among those acceptable.                                                         |
| Option not active | The command refers to an option present in the checkweigher configuration, but not active.                 |
| Absent            | The command refers to an option not present in the checkweigher configuration.                             |

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | (identifier]
ALTERRECIPE=[recipe name) | (identifier]|[value 1]|
ALTERRECIPE=[recipe name) | (identifier] | [value 1]|...|[value n]|
\`\`\`

**Response:**
\`\`\`
ALTERRECIPE=ACCEPTED
ALTERRECIPE=REFUSED|[error code): [error description]: [additional optional
information]
\`\`\`

**Command examples with relative response:**
\`\`\`
ALTERRECIPE=spaghetti500|TARE|1.0
ALTERRECIPE=ACCEPTED
\`\`\`
\`\`\`
ALTERRECIPE=TARE
ALTERRECIPE=REFUSED| 69999:Errore di sintassi
\`\`\`
\`\`\`
ALTERRECIPE=spaghetti500|aaaa
ALTERRECIPE=REFUSED| 69999:Errore di sintassi
\`\`\`
\`\`\`
ALTERRECIPE=spaghetti500|LENGTH|100000.0
ALTERRECIPE=REFUSED|4441:Valori consentiti <= 270.0
\`\`\`
\`\`\`
ALTERRECIPE=spaghetti500|NEW
ALTERRECIPE=REFUSED| 70002:Il file esiste già
\`\`\`
\`\`\`
ALTERRECIPE=spaghetti500|WEIGHT|1000
ALTERRECIPE=ACCEPTED|4454:Parametri di calibrazione non più validi. Valore
calibrato = 500.0, variazione ammessa (±) 10.0
\`\`\`
For additional information regarding the value type, refer to the **Table of the types of values** table.

### 2.26 Recipe parameter identifiers

**Supported on devices:** 12"
The values associated to every recipe data identifier could be various types. In the following syntaxes, at each value is assigned a postfix which defines the type. It is highlighted that such postfix is just an information and, for this reason, it must not be included in the sent command (refer to the examples in the **ALTERRECIPE** paragraph).
Some identifiers are only present in some types of weigher.
There can be various types of error:

\`\`\`
ALTERRECIPE=[recipe name]|EJECTOR_1|[offset INT]|[duration DEC]
\`\`\`
In the example above, it can be seen that the **EJECTOR_1** identifier envisions two values, one INT type and one DEC type. Refer to the **Table of the types of values** for the explanation of the types.

**Table of the types of values**

| Postfix | Description                                                                                               |
| :------ | :-------------------------------------------------------------------------------------------------------- |
| INT     | Integer numerical value without decimal point. The value can be positive, negative or have limits based on the command. |
| BOOL    | Boolean value 0=FALSE, 1=TRUE                                                                             |
| DEC     | Numerical value with decimal point. The value can be positive, negative or have limits based on the command. |
| STR     | Sequence of alphanumerical characters.                                                                    |

The allowed values described in some parameter identifiers, can undergo variations based on the weigher software version, the metal detector model specified or to other limitations.

#### 2.26.1 TARE

**Supported on devices:** 12"
Parameter identifier to consult/modify the tare value of a recipe.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name)|TARE|[DEC value]
\`\`\`

#### 2.26.2 WEIGHT

**Supported on devices:** 12"
Parameter identifier to consult/modify the nominal weight value of a recipe.
The tare value is put at 0 and the --,-,+,++ limits will be forced to LIMIT_TYPE|0 = automatic.
In the case of the weight value which makes the recipe no longer calibrated, the command returns ALTERRECIPE=ACCEPTED| code:error description.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | WEIGHT|[DEC value]
\`\`\`

#### 2.26.3 PRODUCT_CODE

**Supported on devices:** 12"
Parameter identifier to consult/modify the product code.

**Syntax:**
\`\`\`
ALTERRECIPE=PRODUCT_CODE|[STR code]
\`\`\`

#### 2.26.4 LIMITS_VALUE

**Supported on devices:** 12"
Parameter identifier to consult/modify the weight category limits.
The limits set with **LIMITS_VALUE** can be modified if **LIMIT_TYPE** is used.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name] | PRODUCT_CODE|[limit --
DEC] | [limit - DEC] | [limit +
DEC] | [limit ++ DEC]
\`\`\`

#### 2.26.5 LIMIT_TYPE

**Supported on devices:** 12"
Parameter identifier to consult/modify the weight category limits type (see **Table of the type of limit of the weight categories** to visualize allowed values).

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | LIMIT_TYPE | [STR value]
\`\`\`

**Table of the type of limit of the weight categories**

| Value allowed | Description         |
| :------------ | :------------------ |
| AUTO          | Automatic         |
| MAN           | Manual              |
| ADJ_AUTO      | Modifiable automatic |

#### 2.26.6 THROUGHPUT

**Supported on devices:** 12"
Parameter identifier to consult/modify the frequency.
In the case of the frequency value which makes the recipe no longer calibrated, the command returns ALTERRECIPE=ACCEPTED| code:error description.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | THROUGHPUT|[INT value]
\`\`\`

#### 2.26.7 LENGTH

**Supported on devices:** 12"
Parameter identifier to consult/modify the product length, the minimum length and the maximum length of the given product.
In the case of **DEBOUNCING_FILTER=simple**, the minimum valuel|maximum valuel values are not considered and can be omitted.
The **LENGTH** values must always be modified after **DEBOUNCING_FILTER** one.
In the case of the value which makes the recipe no longer calibrated, the command returns ALTERRECIPE=ACCEPTED| code:error description.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | LENGTH|[INT length) | [INT minimum length] | [INT
maximum length]
\`\`\`

#### 2.26.8 DEBOUNCING_FILTER

**Supported on devices:** 12"
Parameter identifier to consult/modify the type of debouncing filter. Refer to **Debouncing filters table**.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | DEBOUNCING_FILTER [STR value]
\`\`\`

**Debouncing filters table**

| Value allowed | Description |
| :------------ | :---------- |
| DISABLED      | Disabled    |
| SIMPLE        | Simple      |
| ENHANCED      | Advanced    |

#### 2.26.9 EJECTOR_1, EJECTOR_2, EJECTOR_3, EJECTOR_4

**Supported on devices:** 12"
Parameter identifier to consult/modify the ejectors configuration.
The checkweigher can manage up to 4 ejectors. Dependently on the customer configuration, only the enabled ejectors can be managed.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | EJECTOR [n] | [offset INT) | [INT length]
\`\`\`

#### 2.26.10 MAXIMUM_CONSECUTIVE_EJECTION

**Supported on devices:** 12"
Parameter identifier to consult/modify the maximum number of products rejected consecutively.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | MAXIMUM_CONSECUTIVE_EJECTION|[INT value]
\`\`\`

#### 2.26.11 PERCENTAGE_OF_PRODUCT_M_TO_ACCEPT

**Supported on devices:** 12"
Parameter identifier to consult/modify the percentage of weight category products - to accept.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name]|PERCENTAGE_OF_PRODUCT_M_TO_ACCEPT|[DEC percentage]
\`\`\`

#### 2.26.12 FBK_ENABLE

**Supported on devices:** 12"
Parameter identifier to enable/disable feedback function.
The parameter is active even if the checkweigher allows feedback
Questo parametro è attivo solo se la pesatrice prevede la gestione feedback.

**Sintassi:**
\`\`\`
ALTERRECIPE=[nome ricetta] |FBK_ENABLE | [valore DEC]
\`\`\`

#### 2.26.13 FBK_TARGET_WEIGHT_ADJUSTER

**Supported on devices:** 12"
Parameter identifier to consult/modify the target weight corrector.
This parameter is active only if the weigher envisions feedback management.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name]|FBK_TARGET_WEIGHT_ADJUSTER|[DEC value]
\`\`\`

#### 2.26.14 FBK_PIECES_TO_AVERAGE

**Supported on devices:** 12"
Parameter identifier to consult/modify the number of products to use for the average.
This parameter is active only if the weigher envisions feedback management.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name]|FBK_PIECES_TO_AVERAGE|[INT value]
\`\`\`

#### 2.26.15 FBK_PIECES_TO_WAIT

**Supported on devices:** 12"
Parameter identifier to consult/modify the number of waiting products.
This parameter is active only if the weigher envisions feedback management.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | FBK_PIECES_TO_WAIT| [INT value]
\`\`\`

#### 2.26.16 FBK_NO_CORRECTION_THRESHOLD

**Supported on devices:** 12"
Parameter identifier to consult/modify the non-correction minimum and maximum thresholds.
This parameter is active only if the weigher envisions feedback management.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | FBK_NOCORRECTION_THRESHOLD|[INT minimum)|[INT
maximum]
\`\`\`

#### 2.26.17 FBK_K_FACTOR

**Supported on devices:** 12"
Parameter identifier to consult/modify the K factor.
This parameter is active only if the weigher envisions feedback management.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | FBK_K_FACTOR| [DEC value]
\`\`\`

#### 2.26.18 FBK_MAXIMUM_CORRECTION

**Supported on devices:** 12"
Parameter identifier to consult/modify the maximum correction.
This parameter is active only if the weigher envisions feedback management.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | FBK_MAXIMUM_CORRECTION| [DEC value]
\`\`\`

#### 2.26.19 FBK_STANDBY_TIME

**Supported on devices:** 12"
Parameter identifier to consult/modify the standby activation time.
This parameter is active only if the weigher envisions feedback management.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name]|FBK_STANDBY_TIME|[INT value]
\`\`\`

#### 2.26.20 FBK_STANDBY_PIECES

**Supported on devices:** 12"
Parameter identifier to consult/modify the products number in post standby waiting.
This parameter is active only if the weigher envisions feedback management.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name]|FBK_STANDBY_PIECES|[INT value]
\`\`\`

#### 2.26.21 FBK_NON_OPERATION_THRESHOLD

**Supported on devices:** 12"
Parameter identifier to consult/modify the no intervention threshold.
This parameter is active only if the weigher envisions feedback management.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name]|FBK_NON_OPERATION_THRESHOLD|[INT value]
\`\`\`

#### 2.26.22 OPTION_A

**Supported on devices:** 12"
Parameter identifier to consult/modify option A.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | OPTION_A|[BOOL value]
\`\`\`

#### 2.26.23 OPTION_B

**Supported on devices:** 12"
Parameter identifier to consult/modify option B.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | OPTION_B|[BOOL value]
\`\`\`

#### 2.26.24 MOTOR_4_SPEED_PERCENTAGE_COMPARED_MOTOR_2

**Supported on devices:** 12"
Parameter identifier to consult/modify the motor 4 speed as a percentage of the motor 2 one.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name] | MOTOR_4_SPEED_PERCENTAGE_COMPARED_MOTOR_2|[INT
value]
\`\`\`

#### 2.26.25 SCREWFEEDER_PTC_IN_OUT_TIMEOUT

**Supported on devices:** 12"
Parameter identifier to consult/modify the timeout connected to the screw-feeder entry and exit photocells.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | SCREWFEEDER_PTC_IN_OUT_TIMEOUT|[INT FTC IN
time]|[INT FTC OUT time]
\`\`\`

#### 2.26.26 METAL_SENSITIVITY

**Supported on devices:** 12"
Parameter identifier to consult/modify the metal detector sensitivity value.
Metal command SE.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | METAL_SENSITIVITY|[INT value]
\`\`\`

#### 2.26.27 METAL_PHASE

**Supported on devices:** 12"
Parameter identifier to consult/modify the metal detector phase or TX program value.
Metal command TP.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | METAL_PHASE|[INT value]
\`\`\`

#### 2.26.28 METAL_FREQUENCY

**Supported on devices:** 12"
Parameter identifier to consult/modify the metal detector frequency or band value.
Metal command BA.

**Values allowed:**
LOW, MEDIUM, HIGH

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | METAL_FREQUENCY|[STR value]
\`\`\`

#### 2.26.29 METAL_ANALISYS_MODE

**Supported on devices:** 12"
Parameter identifier to consult/modify the metal detector analysis mode value.
Metal command AM.

**Values allowed:**
STD, HVI

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name]|METAL_ANALISYS_MODE|[STR value]
\`\`\`

#### 2.26.30 METAL_REVELATION_MODE

**Supported on devices:** 12"
Parameter identifier to consult/modify the metal detector detection mode value.
Metal command DM.

**Values allowed:**
da 0 a 9

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | METAL_REVELATION_MODE| [STR value]
\`\`\`

#### 2.26.31 METAL_Z

**Supported on devices:** 12"
Parameter identifier to consult/modify the metal detector Z variables value.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | METAL_Z|[Z1 INT]|[Z2 INT]|[Z3 INT]|[Z4 INT]|[Z5
INT] | [Z6 INT] | [Z7 INT] | [Z8 INT] | [Z9 INT] | [Z10 INT]|[Z11 INT]|[Z12 INT] | [Z13
INT] | [Z14 INT] | [Z15 INT] | [Z16 INT] | [Z17 INT] | [Z18 INT] | [Z19 INT]
\`\`\`

#### 2.26.32 METAL_TESTER_DIAMETERS

**Supported on devices:** 12"
Parameter identifier to consult/modify the metal detector tester diameters value.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | METAL_TESTER_DIAMETERS|[Ø1 DEC] | [Ø4 DEC] | [Ø3 DEC]
\`\`\`

#### 2.26.33 SPEED_CONVEYOR_BELT_1

**Supported on devices:** 12"
Parameter identifier to consult/modify the weigher conveyor belt 1 speed value.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | SPEED_CONVEYOR_BELT_1|[INT value]
\`\`\`

#### 2.26.34 SPEED_CONVEYOR_BELT_2

**Supported on devices:** 12"
Parameter identifier to consult/modify the weigher conveyor belt 2 speed value.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name]|SPEED_CONVEYOR_BELT_2|[INT value]
\`\`\`

#### 2.26.35 SPEED_CONVEYOR_BELT_3

**Supported on devices:** 12"
Parameter identifier to consult/modify the weigher conveyor belt 3 speed value.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | SPEED_CONVEYOR_BELT_3| [INT value]
\`\`\`

#### 2.26.36 MOTOR_STOP_DELAY_ON_EXIT_PTC

**Supported on devices:** 12"
Parameter identifier to consult/modify the delay value of the weighing belt stop after the engagement of the weigher exit photocell.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | MOTOR_STOP_DELAY_ON_EXIT_PTC|[INT value]
\`\`\`

#### 2.26.37 USRCNT_RESET_VALUE

**Supported on devices:** 12"
Parameter identifier to consult/modify the reset value (Starting value) of the pieces counter.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name]|USRCNT_RESET_VALUE|[INT value]
\`\`\`

#### 2.26.38 USRCNT_ON_EXPIRATION_ACTION

**Supported on devices:** 12"
Parameter identifier to consult/modify the value which represents the action type that must be actuated at the pieces counter expiration. See **Table of executable actions when the counter pieces limit is reached**.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | USRCNT_ON_EXPIRATION_ACTION|[STR value]
\`\`\`

**Table of executable actions when the counter pieces limit is reached**

| Values    | Description                                                                    |
| :-------- | :----------------------------------------------------------------------------- |
| DISABLED  | Disabled                                                                       |
| OUT_TIMED | On the expiration enables the output assigned to the counter                   |
| STOP      | On the expiration stops the checkweigher and enables the notification output |
| FLIP_FLOP | On the expiration flips the status of the output and enables the notification output |

#### 2.26.39 USRCNT_ACTION_RESET

**Supported on devices:** 12"
Parameter identifier to perform the reset operation of the current counter value.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | USRCNT_RESET_VALUE|[INT value]
\`\`\`

#### 2.26.40 USRCNT_OUTPUT_ACTIVATION_TIME

**Supported on devices:** 12"
Parameter identifier to consult/modify the activation period of the output associated to the counter expiration.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | USRCNT_OUTPUT_ACTIVATION_TIME| [INT value]
\`\`\`

#### 2.26.41 USRCNT_NOTIFICATION_ACTIVATION_TIME

**Supported on devices:** 12"
Parameter identifier to consult/modify the activation period of the output associated to the counter expiration notification.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | USRCNT_NOTIFICATION_ACTIVATION_TIME (INT value]
\`\`\`

#### 2.26.42 EXISTS

**Supported on devices:** 12"
Parameter identifier to verify whether a recipe exists.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | EXISTS
\`\`\`

#### 2.26.43 NEW

**Supported on devices:** 12"
Parameter identifier to create a new recipe with default values.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | NEW
\`\`\`
If the recipe already exists, the command returns:
\`\`\`
ALTERRECIPE=REFUSED| 70002:Il file esiste già
\`\`\`

#### 2.26.44 DELETE

**Supported on devices:** 12"
Parameter identifier to delete a new recipe.

**Syntax:**
\`\`\`
ALTERRECIPE=[recipe name) | DELETE
\`\`\`

### 2.27 Consult a recipe with GETFROMRECIPE

**Supported on devices:** 12"
This command allows to obtain information from a recipe contained in the weigher.
The syntax of this command is similar to the **ALTERRECIPE** one and shares with it most of the parameter identifiers and restrictions.

**Syntax:**
\`\`\`
GETFROMRECIPE=[recipe name) | (identifier]
\`\`\`

**Correct response syntax:**
\`\`\`
GETFROMRECIPE=[recipe name) | (identifier] | [value 1]|
GETFROMRECIPE=[recipe name) | (identifier] | [value 1]|...| [value n] |
\`\`\`

**Syntax in case of error:**
\`\`\`
GETFROMRECIPE=REFUSED|[error code]: [error description]: [additional
information]
\`\`\`
For the list of recipe parameter identifiers see **Recipe parameter identifiers** section.
For additional information regarding the types value refer to the **Table of the types of values** table.

**Command examples with relative response:**
\`\`\`
GETFROMRECIPE =spaghetti500|TARE
GETFROMRECIPE =spaghetti500|TARE|0.0
GETFROMRECIPE = spaghetti500|EJECTOR_1
GETFROMRECIPE = spaghetti500|EJECTOR_1|0.0|500
\`\`\`

### 2.28 GET_CURRENT_PIECE_STAT

**Supported on devices:** 12"
This command allows to obtain the medium weight of a range of products passed over the checkweigher.
The average value is given specifying three parameters, the lung dimension which shows the number of last products that has to be considered, samples number shows which products are used to evaluate the average within the lung dimension interval and first element position in range shows if the samples number must start from the end or from the beginning of the lung.
This command always replies with the **PIECE_STAT** message (see **PIECE_STAT** section). In case of insufficient or wrong parameters, the average computed value corresponds to the nominal weight.
The nominal weight values, nominal tare and computed average are expressed in milligrams.

**Syntax:**
\`\`\`
GET_CURRENT_PIECE_STAT=[INT number of samples]|[INT lung dimension]|[intra
range first element position 0=inizio, 1=fine]
\`\`\`

**Response syntax:**
See **PIECE_STAT** section.

**Command examples (given a series of 20 passed product):**
\`\`\`
GET_CURRENT_PIECE_STAT=3|10|0
\`\`\`
The average M is computed over the products 0,1,2 of the lung P.
00,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,
P,P,PP,PP,P,PP,P
,M,M,M
\`\`\`
GET_CURRENT_PIECE_STAT=4|10|1
\`\`\`
The average M is computed over the products 6,7,8,9 of the lung P.
00,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19
P,P,P,P,P,PP,P,P,P
,M,M,M,M
\`\`\`
GET_CURRENT_PIECE_STAT=15|10|0
\`\`\`
The average M is computed over all the products of the lung P (from 0 to 9).
00,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19
P,P,P,P,P,PP,P,P,P
,M,M,M,M,M,M,M,M,M,M
\`\`\`
GET_CURRENT_PIECE_STAT
\`\`\`
No average computed, the average value corresponds to the nominal weight.

### 2.29 PIECE_STAT

**Supported on devices:** 12"
This is not a command, but the answer to the **GET_CURRENT_PIECE_STAT** command.

**Response syntax:**
\`\`\`
PIECE_STAT =[INT nominal weight]|[INT computed mean value]|[INT nominal
tare]|[INT number of samples]|[INT lung dimension]
\`\`\`

### 2.30 STATUS

**Supported on devices:** 12", 7"
**ATTENTION:**
The command described below is outdated, kept in the manual to previous compatibility. We advise against the command usage in favour of **STATSV** command.
Requires the weigher status, for the return codes see **Machine status table**.

**Syntax:**
\`\`\`
STATUS
\`\`\`

**Response:**
\`\`\`
STATUS=STOPPED
\`\`\`
command accepted, the weigher status returns.

**Machine status table**

| Machine Status | Description                                                                                               | Supported on |
| :------------- | :-------------------------------------------------------------------------------------------------------- | :----------- |
| STARTED        | The weigher has started, the belts are moving and adjusted, ready to weigh.                               | 12", 7"      |
| ONSTART        | Weigher started and in motors adjustment phase. In this condition, transit of products is not allowed.    | 12", 7"      |
| STOPPED        | The weigher and its belts are at a standstill.                                                          | 12", 7"      |
| ONERROR        | At least one error has occurred, the errors are listed in the relevant window of the interface.         | 12", 7"      |
| STATIC         | The checkweigher is set in static mode                                                                  | 7"           |
| LOADING        | The checkweigher is starting up                                                                           | 7"           |

### 2.31 BATCHCHANGE

**Supported on devices:** 12", 7"
**ATTENTION:**
The command described below is outdated, kept in the manual to previous compatibility. We advise against the command usage in favour of single commands used to handle batch and recipe configuration. See Chapter 0 to see an example of production change.
Multiple command, it allows to change the active recipe and to activate a new batch associated to the recipe. Some parameters of the batch are also defined: production order, batch code and timeout of the metal tests.
This command closes a possible open batch before performing recipe change (if the recipe name is different from the active one) and to open a new batch.
This command always stops the weigher.

**Syntax:**
1) \`BATCHCHANGE\`
2) \`BATCHCHANGE | [production order] | [batch code] | [recipe) | [time out test metal]\`

**Response:**
1) \`BATCHCHANGE\`
The response to the **BATCHCHANGE** command could be preceded by some **EVENT** notifications which inform regarding a possible closure of an open batch, modification of batch data and opening of a new batch.

**Response 12":**
2) \`EVENT=2018.06.27
16:28:54|old_production_order|old_batch_code|Product100g|LineaTest_1|ID000
00 Cod. 1005|Evento: Chiusura Lotto||
EVENT 2018.06.27
16:33:39|new_production_order|new_batch_code|Product100g|LineaTest_1|ID000
00 Cod. 1004|Evento: Apertura Lotto||
BATCHCHANGE\`

**Response 7":**
2) \`EVENT-2018.06.27
16:28:54|old_production_order|old_batch_code|Product100g|LineaTest_1|ID000
00|Cod. 1005|Evento: Chiusura Lotto||
EVENT 2018.06.27
16:33:39|new_production_order_new_batch_code|Product100g|LineaTest_1|ID000
00 Cod. 1004|Evento: Apertura Lotto||
BATCHCHANGE
EVENT-2021.03.19 12:38:35|
new_production_order_new_batch_code|Product100g|Linea_TestID 01717|Cod.
1007|Event: Batch Modify||
\`\`\`

## 3 Notifications sent by the weigher

In some cases, the weigher can send messages to the customers to notify events or information.
In the description of the syntax of the messages, programming language C style conventions are used to indicate the data type.

**Commands parameters formatting conventions table**

| Format | Description                                                                                                                              |
| :----- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| %s     | Sequence of characters                                                                                                                   |
| %ld    | Integer number, without decimal point                                                                                                    |
| %d     | Integer number, without decimal point                                                                                                    |
| %8.1f  | Number with decimal point; in this case, the number of digits that make up the integer part (8) and the decimal part (1) are specified   |
| %.3f   | Number with decimal point; in this case, only the number of digits that make up the decimal part (3) is specified; the integer part does not have restrictions |
| %1x    | Integer number, without decimal point, expressed in hexadecimal convention                                                               |

### 3.1 Events

#### 3.1.1 EVENT

**Supported on devices:** 12", 7"
The **EVENT** message is sent to notify errors or information, e.g. opening-closing of a production batch.
The **EVENT** message contains the following information: date, time, production order, batch code, recipe name, line code, checkweigher serial number, event code (see **Event codes table**), event description, name and surname of the authenticated user (not managed in all software versions). Each information is separated by the character (ASCII 0x7C).

**Syntax:**
\`\`\`
EVENT=[date and time in format yyyy/mm/dd hh:mm:ss]|[production order]|[batch
code]|[recipe) | [linecode) | [checkweigher SN] | [event code] | [event
description] | [operator]|
\`\`\`

**Example:**
\`\`\`
EVENT-2014/3/21 16:30:00|ordp|codlot|biscuit recipe|codlin|ID00019|Cod.
1004|Evento: AperturaLotto | Nomel Cognome1|
\`\`\`

**Event codes table**

| Event code | Description                                     |
| :--------- | :---------------------------------------------- |
| 1000       | Errors reset                                    |
| 1001       | Recipe change active                            |
| 1002       | Recipe change not possible                      |
| 1003       | Modified recipe                                 |
| 1004       | Batch opening                                   |
| 1005       | Batch closure                                   |
| 1006       | Batch change                                    |
| 1007       | Modified batch                                  |
| 1008       | Command not recognised                          |
| 1009       | Metal test performed                            |
| 1010       | Modification in general setup                   |
| 1011       | Command not performed, checkweigher not in remote mode |
| 1012       | Checkweigher mode change: LOCAL, REMOTE, MAINTENANCE |
| 1013       | Modification in alarms setup (deactivated option) |
| 1014       | Modification in alarms setup (stop option)      |
| 1015       | Modification in ejectors setup                  |
| 1016       | Shutdown requested by UPS                       |
| Altri valori | A different value to those present in this table represent an error code. Every error is identified by a unique code. The error description will be present in the description part. |

### 3.2 Statistics

#### 3.2.1 STATP

**Supported on devices:** 12", 7" (48,49,50 fields are not defined)
The **STATP** message is sent to notify the production statistics. It can be sent following the **STATREQ** request or autonomously at regular intervals if activated via **ENABLESTATS** and configurated via **SELSTATSANSWER** (this message is the configuration default value of **SELSTATSANSWER**).

**Syntax:**
\`\`\`
STATP=%s%s%s%s%s%s%s%ld %ld %8.1f|%8.1f|%8.1f|%ld %ld %ld %ld %ld %ld|
%d%d%d%d%.1f|%sg|%8.1f|%s%ld %ld %s%8.1f|%8.1f|%8.1f|%ld %ld %ld %ld %l
d|%ld|%d%d%d%d%.1f|sg|%8.1f|%s%s|
\`\`\`

**Note:**
In the description of the fields that follows, the descriptions appear with the wording "incremental". Incremental means the value with respect to that of the last statistics sent.

**STATP notification parameters table**

| Position of the field | Description                                                                                             |
| :-------------------- | :------------------------------------------------------------------------------------------------------ |
| 1                     | Date and time                                                                                           |
| 2                     | Batch start date and time                                                                               |
| 3                     | Production order                                                                                        |
| 4                     | Production code                                                                                         |
| 5                     | Recipe name                                                                                             |
| 6                     | Line code                                                                                               |
| 7                     | Checkweigher serial number                                                                              |
| 8                     | Total products                                                                                          |
| 9                     | Total accepted                                                                                          |
| 10                    | Products average weight accepted                                                                        |
| 11                    | Products minimum weight accepted                                                                        |
| 12                    | Products maximum weight accepted                                                                        |
| 13                    | Total - category products rejected (total transited - accepted)                                         |
| 14                    | Total -- category products rejected (total transited – accepted)                                        |
| 15                    | Total + category products rejected (total transited - accepted)                                         |
| 16                    | Total ++ category products rejected (total transited – accepted)                                        |
| 17                    | Total category products that cannot be weighed                                                          |
| 18                    | Total metal category products                                                                           |
| 19                    | Test metal, number of tests performed                                                                   |
| 20                    | Test metal, number of tests passed                                                                      |
| 21                    | Test metal, number of tests failed                                                                      |
| 22                    | Test metal, number of tests refused                                                                     |
| 23                    | Last weight (exact value)                                                                               |
| 24                    | Last weight (rounded value)                                                                             |
| 25                    | Last weight difference                                                                                  |
| 26                    | Last weight class (NOT AVAIL, EXPELLED, WEIGHT_MM, WEIGHT_M, WEIGHT_PP, WEIGHT_P, WEIGHT_OK, WEIGHT_OK_LOW) |
| 27                    | Total incremental products                                                                              |
| 28                    | Total incremental accepted                                                                              |
| 29                    | Incremental date time                                                                                   |
| 30                    | Incremental OK products average weight                                                                  |
| 31                    | Incremental OK products minimum weight                                                                  |
| 32                    | Incremental OK products maximum weight                                                                  |
| 33                    | Total incremental - category products rejected                                                          |
| 34                    | Total incremental -- category products rejected                                                         |
| 35                    | Total incremental + category products rejected                                                          |
| 36                    | Total incremental ++ category products rejected                                                         |
| 37                    | Total incremental category products that cannot be weighed                                              |
| 38                    | Total incremental metal category products                                                               |
| 39                    | Number of incremental metal tests performed                                                             |
| 40                    | Number of incremental metal tests passed                                                                |
| 41                    | Number of incremental metal tests failed                                                                |
| 42                    | Number of incremental metal tests refused                                                               |
| 43                    | Last incremental weight (exact value)                                                                   |
| 44                    | Last incremental weight (rounded value)                                                                 |
| 45                    | Last incremental weight difference                                                                      |
| 46                    | Last incremental weight class (NOT AVAIL, EXPELLED, WEIGHT_MM, WEIGHT_M, WEIGHT_PP, WEIGHT_P, WEIGHT_OK, WEIGHT_OK_LOW) |
| 47                    | Name and surname of the authenticated user                                                              |
| 48                    | Total OK- category products                                                                             |
| 49                    | Total OK- category products accepted                                                                    |
| 50                    | Standard deviation value within the batch                                                               |

#### 3.2.2 STATPATB

**Supported on devices:** 12", 7" (39,40 fields are not defined)
The **STATPATB** message is sent to notify the production statistics. It can be sent following the **STATREQATB** request or autonomously at regular intervals if activated via **ENABLESTATS** and configurated via **SELSTATSANSWER**.

**Syntax:**
\`\`\`
STATPATB=%s%s%s%s%s%s%s|%ld|%ld|%8.1f|%8.1f|%8.1f|%ld|%ld %ld %ld %ld|%
ld|%d%d%d%d%.1f|sg|%8.1f|%s%s%.3f|%ld %ld %ld %ld %ld %ld %ld %ld %ld|
%ld|
\`\`\`

**STATPATB notification parameters table**

| Field | Description                                                                                                                              |
| :---- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Date and time                                                                                                                            |
| 2     | Batch start date and time                                                                                                                |
| 3     | Production order                                                                                                                         |
| 4     | Production code                                                                                                                          |
| 5     | Recipe name                                                                                                                              |
| 6     | Line code                                                                                                                                |
| 7     | Checkweigher serial number                                                                                                               |
| 8     | Total products                                                                                                                           |
| 9     | Total accepted                                                                                                                           |
| 10    | Products average weight accepted                                                                                                         |
| 11    | Products minimum weight accepted                                                                                                         |
| 12    | Products maximum weight accepted                                                                                                         |
| 13    | Total - category products rejected (total transited - accepted)                                                                          |
| 14    | Total -- category products rejected (total transited - accepted)                                                                         |
| 15    | Total + category products rejected (total transited - accepted)                                                                          |
| 16    | Total ++ category products rejected (total transited – accepted)                                                                         |
| 17    | Total category products that cannot be weighed                                                                                           |
| 18    | Total metal category products                                                                                                            |
| 19    | Test metal, number of tests performed                                                                                                    |
| 20    | Test metal, number of tests passed                                                                                                       |
| 21    | Test metal, number of tests failed                                                                                                       |
| 22    | Test metal, number of tests refused                                                                                                      |
| 23    | Last weight (exact value)                                                                                                                |
| 24    | Last weight (rounded value)                                                                                                              |
| 25    | Last weight difference                                                                                                                   |
| 26    | Last weight class (NOT AVAIL, EXPELLED, WEIGHT_MM, WEIGHT_M, WEIGHT_PP, WEIGHT_P, WEIGHT_OK, WEIGHT_OK_LOW)                               |
| 27    | Name and surname of the authenticated user                                                                                               |
| 28    | The standard deviation value of the entire batch                                                                                         |
| 29    | Total OK category products                                                                                                               |
| 30    | Total - category products (total products of this category transited on the checkweigher; to find out whether the products in this category have been accepted or rejected, refer to field 13, which indicates how many have been rejected) |
| 31    | Total -- category products (total products of this category transited on the checkweigher; to find out whether the products in this category have been accepted or rejected, refer to field 14, which indicates how many have been rejected) |
| 32    | Total + category products (total products of this category transited on the checkweigher; to find out whether the products in this category have been accepted or rejected, refer to field 15, which indicates how many have been rejected) |
| 33    | Total ++ category products (total products of this category transited on the checkweigher; to find out whether the products in this category have been accepted or rejected, refer to field 16, which indicates how many have been rejected) |
| 34    | Total OK category products                                                                                                               |
| 35    | Total products accepted of the - category                                                                                                |
| 36    | Total products accepted of the -- category                                                                                               |
| 37    | Total products accepted of the + category                                                                                                |
| 38    | Total products accepted of the ++ category                                                                                               |
| 39    | Total OK- category products                                                                                                              |
| 40    | Total OK- category products accepted                                                                                                     |

### 3.3 Recipe data:

#### 3.3.1 INFORECIPE

**Supported on devices:** 12", 7"
The **INFORECIPE** message is sent following an **INFORECIPE** request command.

**Syntax:**
\`\`\`
INFORECIPE=%s|prod.code %s|weight %.1f|tare %.1f|lim- %.1f|lim+ %.1f|lim--
%.1f|lim++ %.1f|
\`\`\`

**INFORECIPE notification parameters table**

| Field       | Description                          |
| :---------- | :----------------------------------- |
| %s          | Name of the current recipe           |
| prod.code=%s | Product code contained in the recipe |
| Weight=%.1f | Nominal weight of the product        |
| Tare=%.1f   | Tare                                 |
| lim-=%.1f   | Limit value -. (tolerance)           |
| lim+=%.1f   | Limit value +. (tolerance)           |
| lim--=%.1f  | Limit value --. (tolerance)          |
| lim++=%.1f  | Limit value ++. (tolerance)          |

### 3.4 Weighings:

#### 3.4.1 Individual weighing WEIGHT

**Supported on devices:** 12", 7"
The **WEIGHT** message is sent following a new weighing.
Sending the **WEIGHT** message must be enabled; as default settings it is disabled.

**Syntax:**
\`\`\`
WEIGHT=%s%s%s%s%s%s%ld %ld %lx|
\`\`\`

**Example:**
\`\`\`
WEIGHT=2018.06.28
12:11:31:0576|ordine_produzione|codice_lotto|Prodotto100g|LineaTest_1|ID00000
|100000|0|80|
\`\`\`

**WEIGHT notification parameters table**

| Field | Description                                                                                             |
| :---- | :------------------------------------------------------------------------------------------------------ |
| %s    | Date (yyyy.mm.dd), time (hh:mm:ss:msec)                                                                 |
| %s    | Production order of the active batch                                                                    |
| %s    | Production code of the active batch                                                                     |
| %s    | Name of the current recipe                                                                              |
| %s    | Line code                                                                                               |
| %s    | Checkweigher serial number                                                                              |
| %ld   | Weight detected expressed in milligrams                                                                 |
| %ld   | Weight detected - nominal weight                                                                        |
| %1x   | Classification of the weight (see **Weights classification table**), the value can be a combination of several bit |

**Weights classification table**

| Bit | Weights classification                                                                                |
| :-- | :---------------------------------------------------------------------------------------------------- |
| 0   | Product too long                                                                                      |
| 1   | Product too short                                                                                     |
| 2   | Metal                                                                                                 |
| 3   | Weight of ++ category                                                                                 |
| 4   | Weight of + category                                                                                  |
| 5   | Weight of -- category                                                                                 |
| 6   | Weight of - category                                                                                  |
| 7   | Weight of OK category                                                                                 |
| 8   | Expelled                                                                                              |
| 9   | Product too close                                                                                     |
| 10  | Weight detected with new dynamic tare                                                                 |
| 11  | Weight condition detected with incorrect tare (weight ignored)                                        |
| 12  | Weight outside capacity, above the maximum limit                                                      |
| 13  | Weight outside capacity, below the minimum limit                                                      |
| 14  | Category weight - accepted if: 1 - category expulsion configured 2 "save n% of - category products" option enabled 3 average error >0 |
| 15  | Product expelled if: 1 no upstream consent 2 products reject enabled due to no upstream consent       |
| 16  | Invalid weight indicated by pre-weighing equipment                                                    |
| 17  | The weight lies within the OK category and it is above the nominal weight                             |
| 18  | The weight lies within the OK category and it is below the nominal weight                             |

**Examples of weight classification:**
\`\`\`
flag = 0x80: OK, rientra nella categoria OK
flag = 0x10080: OK e OK-, rientra nella categoria OK ma è inferiore al peso
nominale
flag = 0x10: +, rientra nella categoria +
flag = 0x120: -- e scartato, rientra nella categoria -- ed è stato espulso
\`\`\`

### 3.5 Batches and production

#### 3.5.1 Information of the BATCHINFO batch

**Supported on devices:** 12", 7"
The **BATCHINFO** message is sent following a new **BATCHINFO** request, see **BATCHINFO** section.

#### 3.5.2 EndOfBatch batch closing notification

**Supported on devices:** 12", 7"
The **EndOfBatch** message is sent before a batch closure event to notify the final statistics of the batch closing.

**Syntax:**
\`\`\`
EndOfBatch= %s/%s %s %s %s%s %s/%s/%s %s:%s%s %s/%s/%s %s:%s%s %s
%.1f%s %.1f%s %.1f%s |
%s %s%s%ld %s %s %s %s %ld %s %ld %s %ld %s
%.1f%s %.1f%s %.1f%s %ld %ld %ld %ld %ld %ld %ld %ld %ld %ld|
%ld %ld %ld %ld %ld %ld %ld %.3f%s %.2f%s %.2f%s %.2f%s %s|
\`\`\`
In the **EndOfBatch message fields table** that follows, the **Overall or batch** column indicates whether the value refers to the overall batch (or production) or to the current split batch.
If the split batch is not being used, all fields will refer to the overall batch.

**EndOfBatch message fields table**

| Pos | Field   | Description                                                                                             | Overall or batch |
| :-- | :------ | :------------------------------------------------------------------------------------------------------ | :--------------- |
| 1   | %s      | Type of batch (GLOBAL, SPLIT)                                                                           |                  |
| 2   | %s      | Name of the batch PDF file                                                                              |                  |
| 3   | %s      | Checkweigher model                                                                                      |                  |
| 4   | %s      | Checkweigher serial number                                                                              |                  |
| 5   | %s      | Checkweigher machine code                                                                               |                  |
| 6   | %s      | Line code                                                                                               |                  |
| 7   | %s      | Date (yyyy/mm/dd) and time (hh:mm.ss) of batch start                                                    |                  |
| 8   | %s      | Date (yyyy/mm/dd) and time (hh:mm.ss) of batch end                                                      |                  |
| 9   | %s      | Operator                                                                                                |                  |
| 10  | %s      | Production code                                                                                         |                  |
| 11  | %s      | Production order                                                                                        |                  |
| 12  | %s      | Production type (PIECES, MINUTES, MANUAL)                                                               |                  |
| 13  | %ld     | Number associated to the production type                                                                |                  |
| 14  | %s      | Recipe                                                                                                  |                  |
| 15  | %s)     | Extra 1 batch field                                                                                     |                  |
| 16  | %s      | Extra 2 batch field                                                                                     |                  |
| 17  | %s      | Product code                                                                                            |                  |
| 18  | %ld%s   | Product length and unit of measurement                                                                  |                  |
| 19  | %ld%s   | Product minimum length and unit of measurement                                                          |                  |
| 20  | %ld%s   | Product maximum length and unit of measurement                                                          |                  |
| 21  | %.1f%s  | Nominal weight and unit of measurement                                                                  |                  |
| 22  | %.1f%s  | Tare and unit of measurement                                                                            |                  |
| 23  | %.1f%s  | Limit ++ and unit of measurement                                                                        |                  |
| 24  | %.1f%s  | Limit + and unit of measurement                                                                         |                  |
| 25  | %.1f%s  | Limit - and unit of measurement                                                                         |                  |
| 26  | %.1f%s  | Limit -- and unit of measurement                                                                        |                  |
| 27  | %ld     | Total products ++                                                                                       | Overall          |
| 28  | %ld     | Total products +                                                                                        | Overall          |
| 29  | %ld     | Total OK- products (OK minus), if "Batch average weight dynamic control" option enabled                   | Overall          |
| 30  | %ld     | Total products OK                                                                                       | Overall          |
| 31  | %ld     | Total products -                                                                                        | Overall          |
| 32  | %ld     | Total products --                                                                                       | Overall          |
| 33  | %ld     | General total                                                                                           | Overall          |
| 34  | %ld     | Total products accepted                                                                                 | Overall          |
| 35  | %ld     | Total products that cannot be weighed                                                                   | Overall          |
| 36  | %ld     | Total metal products                                                                                    | Overall          |
| 37  | %ld     | Total products accepted ++                                                                              | Batch            |
| 38  | %ld     | Total products accepted +                                                                               | Batch            |
| 39  | %ld     | Total OK- accepted (OK minus), if "Batch average weight dynamic control" option enabled                   | Batch            |
| 40  | %ld     | Total products accepted OK                                                                              | Batch            |
| 41  | %ld     | Total products accepted -                                                                               | Batch            |
| 42  | %ld     | Total products accepted --                                                                              | Batch            |
| 43  | %ld     | Total products accepted                                                                                 | Batch            |
| 44  | %.3f%s  | Standard deviation                                                                                      |                  |
| 45  | %.2f%s  | Average error                                                                                           |                  |
| 46  | %.2f%s  | Medium error                                                                                            |                  |
| 47  | %.2f%s  | Total weight of the products accepted                                                                   |                  |
| 48  | %s      | In the case of the "Negative batch acceptance control" option and batch average lower than the nominal weight, it contains BATCH<0 |                  |

### 3.6 Date and time

#### 3.6.1 Actual date and time DATETIME

**Supported on devices:** 12", 7"
The **DATETIME** message is sent following a variation of the date and time.
The date and time can be changed directly from the weigher user interface or via the **DATETIME** command.

**Syntax:**
\`\`\`
DATETIME=%2d/%2d/%4d|%2d:%2d:%2d.%3d|
DATETIME=[dd/mm/yyyy|hh:mm:ss.msec]
\`\`\`
In case of failure, based on the used device, one of the following errors will be raised:

**12" devices error syntax:**
\`\`\`
DATETIME=REFUSED| [refuse reason]
\`\`\`

**7" devices error syntax:**
\`\`\`
ERRCMD
\`\`\`

## 4 Example of communication

### 4.1 Example of weights and statistics sending

Figure 2: Communication example - Weights and statistics sending.
(Diagram shows client sending STATSV, receiving STATSV responses, then sending SELSTATSANSWER=STATP, STATCADENCY=60, BATCHSTART, receiving EVENTs and finally STATP and WEIGHT messages after ENABLESTATS)

### 4.2 Example of production change

Figure 3: Communication example - Production change, editing recipe and batch data.
(Diagram shows a sequence starting with STATSV, STOP, BATCHSTOP, GETRECIPELIST, RECIPE=Product100g, BATCHINFO, BATCHMODIFY=OPERATOR|Marco Rossi, BATCHSTART, and monitoring STATSV status changes throughout.)

## 5 Index of the tables

*   DETAILED MACHINE STATUS TABLE
*   BATCH DATA IDENTIFIERS TABLE
*   BATCHINFO PARAMETERS TABLE
*   MASK FOR FILTER OF THE MESSAGES SENT BY THE WEIGHER.
*   TABLE OF DATETIME PARAMETERS..
*   TABLE OF EXAMPLES OF FORMATTING OF NUMERICAL VALUES.
*   TABLE OF THE TYPES OF ALTERRECIPE COMMAND ERRORS
*   TABLE OF THE TYPES OF VALUES
*   TABLE OF THE TYPE OF LIMIT OF THE WEIGHT CATEGORIES
*   DEBOUNCING FILTERS TABLE
*   TABLE OF EXECUTABLE ACTIONS WHEN THE COUNTER PIECES LIMIT IS REACHED
*   MACHINE STATUS TABLE
*   COMMANDS PARAMETERS FORMATTING CONVENTIONS TABLE
*   EVENT CODES TABLE
*   STATP NOTIFICATION PARAMETERS TABLE.
*   STATPATB NOTIFICATION PARAMETERS TABLE
*   INFORECIPE NOTIFICATION PARAMETERS TABLE
*   WEIGHT NOTIFICATION PARAMETERS TABLE
*   WEIGHTS CLASSIFICATION TABLE
*   ENDOFBATCH MESSAGE FIELDS TABLE..

## 6 Index of the commands and notifications

### A
*   ALTERRECIPE;

### B
*   BATCHCHANGE;
*   BATCHINFO;
*   BATCHMODIFY;
*   BATCHSTART;
*   BATCHSTOP;

### D
*   DATETIME;
*   DEBOUNCING_FILTER;
*   DELETE;
*   DISABLESTATS;

### E
*   EJECTOR_1, EJECTOR_2, EJECTOR_3, EJECTOR_4;
*   ENABLESTARTBUTTON;
*   ENABLESTATS;
*   EndOfBatch;
*   ERRNUM;
*   EVENT;
*   EXISTS;

### F
*   FBK_ENABLE;
*   FBK_K_FACTOR;
*   FBK_MAXIMUM_CORRECTION;
*   FBK_NO_CORRECTION_THRESHOLD;
*   FBK_NON_OPERATION_THRESHOLD;
*   FBK_PIECES_TO_AVERAGE;
*   FBK_PIECES_TO_WAIT;
*   FBK_STANDBY_PIECES;
*   FBK_STANDBY_TIME;
*   FBK_TARGET_WEIGHT_ADJUSTER;

### G
*   GET_CURRENT_PIECE_STAT.;
*   GETFROMRECIPE.;
*   GETRECIPELIST;

### I
*   INFORECIPE;

### L
*   LENGTH;
*   LIMIT_TYPE;
*   LIMITS_VALUE;
*   LINECODE;

### M
*   MAXIMUM_CONSECUTIVE_EJECTION;
*   METAL_ANALISYS_MODE;
*   METAL_FREQUENCY;
*   METAL_PHASE;
*   METAL_REVELATION_MODE;
*   METAL_SENSITIVITY;
*   METAL_TESTER_DIAMETERS;
*   METAL_Z;
*   MOTOR_4_SPEED_PERCENTAGE_COMPARED_MOTOR_2;
*   MOTOR_STOP_DELAY_ON_EXIT_PTC;
*   MSGFILTER;

### N
*   NEW;

### O
*   OPTION_A;
*   OPTION_B;

### P
*   PERCENTAGE_OF_PRODUCT_M_TO_ACCEPT;
*   PIECE_STAT.;
*   PRODUCT_CODE;

### R
*   RECIPE;
*   RESETERRORI;

### S
*   SCREWFEEDER_PTC_IN_OUT_TIMEOUT;
*   SELSTATSANSWER;
*   SHOWMESSAGE;
*   SHUTDOWN;
*   SPEED_CONVEYOR_BELT_1;
*   SPEED_CONVEYOR_BELT_2;
*   SPEED_CONVEYOR_BELT_3;
*   START;
*   STATCADENCY;
*   STATP;
*   STATPATB;
*   STATREQ;
*   STATREQATB;
*   STATSV;
*   STATUS;
*   STOP;

### T
*   TARE;
*   THROUGHPUT;

### U
*   USRCNT_ACTION_RESET;
*   USRCNT_ON_EXPIRATION_ACTION;
*   USRCNT_OUTPUT_ACTIVATION_TIME;
*   USRCNT_RESET_VALUE;

### W
*   WEIGHT;
