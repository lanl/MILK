#!/bin/sh

MAUD_PATH=$1
lib=$MAUD_PATH/Java
$MAUD_PATH/PlugIns/Home/bin/java -mx8196M -cp "$lib/*" com.radiographema.MaudText -file $2

sleep 3 