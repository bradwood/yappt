#!/bin/sh
set -e

if tmux has-session -t=yappt 2> /dev/null; then
  tmux attach -t yappt
  exit
fi

tmux new-session -d -s yappt -n vim -x $(tput cols) -y $(tput lines)


tmux send-keys -t yappt:vim "pipenv shell" Enter
tmux split-window -t yappt:vim -h
tmux send-keys -t yappt:vim "pipenv shell" Enter
tmux split-window -t yappt:vim.2 -v
tmux send-keys -t yappt:vim.3 "pipenv shell" Enter
sleep 5
tmux send-keys -t yappt:vim.1 "vim -c CommandTBoot" Enter
tmux send-keys -t yappt:vim.2 "git status" Enter
tmux attach -t yappt:vim.1
