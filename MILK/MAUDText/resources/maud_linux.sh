#!/bin/sh

MAUD_PATH=$1
lib=$MAUD_PATH/lib
$MAUD_PATH/jdk/bin/java -mx8196M -cp "$lib/*" com.radiographema.MaudText -file $2
