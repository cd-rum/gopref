#!/bin/zsh

for i in {120639..120643}

do
	curl -k https://gopref.advpls.com/api/documents\?id\=$i
done
