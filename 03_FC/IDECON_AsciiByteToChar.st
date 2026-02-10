// ==============================================================================
// FUNZIONE: IDECON_AsciiByteToChar
// DESCRIZIONE: Converte un Byte ASCII nel corrispondente carattere Stringa
// ==============================================================================

// Variabili Interne (Dichiarare in Sysmac):
// u : USINT

u := BYTE_TO_USINT(InByte);

CASE u OF
    16#20: IDECON_AsciiByteToChar := ' ';
    16#2D: IDECON_AsciiByteToChar := '-';
    16#2E: IDECON_AsciiByteToChar := '.';
    16#2F: IDECON_AsciiByteToChar := '/';
    16#3A: IDECON_AsciiByteToChar := ':';
    16#3D: IDECON_AsciiByteToChar := '=';
    16#3F: IDECON_AsciiByteToChar := '?';
    16#5F: IDECON_AsciiByteToChar := '_';
    16#7C: IDECON_AsciiByteToChar := '|';
    16#30: IDECON_AsciiByteToChar := '0';
    16#31: IDECON_AsciiByteToChar := '1';
    16#32: IDECON_AsciiByteToChar := '2';
    16#33: IDECON_AsciiByteToChar := '3';
    16#34: IDECON_AsciiByteToChar := '4';
    16#35: IDECON_AsciiByteToChar := '5';
    16#36: IDECON_AsciiByteToChar := '6';
    16#37: IDECON_AsciiByteToChar := '7';
    16#38: IDECON_AsciiByteToChar := '8';
    16#39: IDECON_AsciiByteToChar := '9';
    16#41: IDECON_AsciiByteToChar := 'A';
    16#42: IDECON_AsciiByteToChar := 'B';
    16#43: IDECON_AsciiByteToChar := 'C';
    16#44: IDECON_AsciiByteToChar := 'D';
    16#45: IDECON_AsciiByteToChar := 'E';
    16#46: IDECON_AsciiByteToChar := 'F';
    16#47: IDECON_AsciiByteToChar := 'G';
    16#48: IDECON_AsciiByteToChar := 'H';
    16#49: IDECON_AsciiByteToChar := 'I';
    16#4A: IDECON_AsciiByteToChar := 'J';
    16#4B: IDECON_AsciiByteToChar := 'K';
    16#4C: IDECON_AsciiByteToChar := 'L';
    16#4D: IDECON_AsciiByteToChar := 'M';
    16#4E: IDECON_AsciiByteToChar := 'N';
    16#4F: IDECON_AsciiByteToChar := 'O';
    16#50: IDECON_AsciiByteToChar := 'P';
    16#51: IDECON_AsciiByteToChar := 'Q';
    16#52: IDECON_AsciiByteToChar := 'R';
    16#53: IDECON_AsciiByteToChar := 'S';
    16#54: IDECON_AsciiByteToChar := 'T';
    16#55: IDECON_AsciiByteToChar := 'U';
    16#56: IDECON_AsciiByteToChar := 'V';
    16#57: IDECON_AsciiByteToChar := 'W';
    16#58: IDECON_AsciiByteToChar := 'X';
    16#59: IDECON_AsciiByteToChar := 'Y';
    16#5A: IDECON_AsciiByteToChar := 'Z';
    16#61: IDECON_AsciiByteToChar := 'a';
    16#62: IDECON_AsciiByteToChar := 'b';
    16#63: IDECON_AsciiByteToChar := 'c';
    16#64: IDECON_AsciiByteToChar := 'd';
    16#65: IDECON_AsciiByteToChar := 'e';
    16#66: IDECON_AsciiByteToChar := 'f';
    16#67: IDECON_AsciiByteToChar := 'g';
    16#68: IDECON_AsciiByteToChar := 'h';
    16#69: IDECON_AsciiByteToChar := 'i';
    16#6A: IDECON_AsciiByteToChar := 'j';
    16#6B: IDECON_AsciiByteToChar := 'k';
    16#6C: IDECON_AsciiByteToChar := 'l';
    16#6D: IDECON_AsciiByteToChar := 'm';
    16#6E: IDECON_AsciiByteToChar := 'n';
    16#6F: IDECON_AsciiByteToChar := 'o';
    16#70: IDECON_AsciiByteToChar := 'p';
    16#71: IDECON_AsciiByteToChar := 'q';
    16#72: IDECON_AsciiByteToChar := 'r';
    16#73: IDECON_AsciiByteToChar := 's';
    16#74: IDECON_AsciiByteToChar := 't';
    16#75: IDECON_AsciiByteToChar := 'u';
    16#76: IDECON_AsciiByteToChar := 'v';
    16#77: IDECON_AsciiByteToChar := 'w';
    16#78: IDECON_AsciiByteToChar := 'x';
    16#79: IDECON_AsciiByteToChar := 'y';
    16#7A: IDECON_AsciiByteToChar := 'z';
ELSE
    IDECON_AsciiByteToChar := '?';
END_CASE;