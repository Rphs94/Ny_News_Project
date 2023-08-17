while [ ! -f /home/check/finish.txt ]; do
  sleep 1
  echo "Waiting for finish.txt to be created..."
done