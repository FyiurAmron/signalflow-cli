#!/bin/zsh
for ((i = $1; i < $2; i += 2)) do
    echo && echo Slice $((i)) to $((i+2))
    cmd="time ./sfx.sh -x -a $((i))00000000 -o $((i+2))00000000 -r 1m --output events $3"
    eval $cmd
done
