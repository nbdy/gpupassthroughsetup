tested on: 
- ubuntu 16.04 (elementary 0.4)
- ubuntu 18.04 (elementary 5.0) 
- debian 10 (Parrot 4.8)
<br>

currently just supports this hardware constellation:<br>
cpu: intel / amd<br>
guest gpu: amd / ati<br> 
host gpu: nvidia<br>
### notice
i'm not liable if your system decides to end it's existence.<br>
check the files the 'setup.py' modifies.<br>
<br>
for example after running 'sudo python3 setup.py -i intel -g amd':
- '/etc/default/grub' (for me) usually contains only 2 pci ids

but after running 'sudo python3 setup.py -i intel -g ati':
- '/etc/default/grub' (for me) contains a lot of pci ids, which would not be correct
- usually there should be two pci ids
- check lscpi -knn | grep "{pciid}" to know which ones to remove

### fs*
[*fs][frequent statements]<br>

s: after rebooting there is no sound<br>
a: check modified files and confirm only gpu is in pci ids, your soundcard could also be manufactured be amd or ati<br>
<br>
