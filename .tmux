#!/bin/sh
set -e

# change this to the name of this project
TMUX_SESS_NAME=yappt
# change this to the name of the first tmux window
TMUX_WIN1_NAME=vim

export NVIM_LISTEN_ADDRESS=/tmp/nvimsocket.$TMUX_SESS_NAME

if tmux has-session -t=$TMUX_SESS_NAME 2> /dev/null; then
  tmux attach -t $TMUX_SESS_NAME
  exit
fi

tmux new-session -d -s $TMUX_SESS_NAME -n $TMUX_WIN1_NAME -x $(tput cols) -y $(tput lines)

tmux send-keys -t $TMUX_SESS_NAME:$TMUX_WIN1_NAME "pipenv shell" Enter
tmux split-window -t $TMUX_SESS_NAME:$TMUX_WIN1_NAME -h
tmux send-keys -t $TMUX_SESS_NAME:$TMUX_WIN1_NAME "pipenv shell" Enter
tmux split-window -t $TMUX_SESS_NAME:$TMUX_WIN1_NAME.2 -v
tmux send-keys -t $TMUX_SESS_NAME:$TMUX_WIN1_NAME.3 "pipenv shell" Enter

sleep 5
tmux send-keys -t $TMUX_SESS_NAME:$TMUX_WIN1_NAME.1 "vim -c CommandTBoot" Enter
tmux send-keys -t $TMUX_SESS_NAME:$TMUX_WIN1_NAME.2 "git status" Enter
tmux attach -t $TMUX_SESS_NAME:$TMUX_WIN1_NAME.1
