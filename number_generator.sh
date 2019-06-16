#! /bin/bash
for i in {1..142}
do
   echo -n "\"$i\","
done
echo ""
for i in {1..142}
do
   echo -n "false,"
done
echo ""
for i in {1..142}
do
   echo -n "true,"
done
