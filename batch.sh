#!/bin/zsh

for i in {120639..120643}

do
	echo $i
	curl -k https://gopref.advpls.com/api/documents\?id\=$i
done
