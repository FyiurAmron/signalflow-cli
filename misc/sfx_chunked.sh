#!/bin/zsh
for ((i = $2; i < $3; i += 2)) do
    echo && echo Slice $((i)) to $((i+2))
    cmd="time ./sfx.sh -t $1 -x -a $((i))00000000 -o $((i+2))00000000 -r 1m --output events $4"
    eval $cmd
done
