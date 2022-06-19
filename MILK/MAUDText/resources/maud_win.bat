@ECHO

SET MAUD_PATH=%1
SET LIB=%MAUD_PATH%\lib
%MAUD_PATH%\jdk\bin\java -mx8196M --add-opens java.base/java.net=ALL-UNNAMED -cp "%LIB%\*" com.radiographema.MaudText -file %2
