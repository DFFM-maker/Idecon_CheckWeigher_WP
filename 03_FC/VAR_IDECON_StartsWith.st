VAR internal
pLen	UINT			False	False	
prefixLenU	UINT			False	False	
prefixLen	INT			False	False	
textLen	INT			False	False	
VAR IN/OUT
EN	Input	BOOL	No Edge		False	False	
InText	Input	STRING[512]	No Edge		False	False	
Prefix	Input	STRING[64]	No Edge		False	False	
	
Var RETURN
IDECON_StartsWith	BOOL	
