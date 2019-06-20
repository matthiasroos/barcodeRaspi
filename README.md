# Debugging from remote machine


sudo ln -s ~pi/.Xauthority /root/.Xauthority

to redirect the screen output back:
export DISPLAY=:0

sudo vi /etc/ssh/sshd_config
PubkeyAuthentication yes

sudo /etc/init.d/ssh restart

on ssh host:
ssh-copy-id -i ~/.ssh/mykey user@host


