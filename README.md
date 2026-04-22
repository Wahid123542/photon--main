sudo# Photon main (team 20)
[quick link to the main branch](https://github.com/SE-Team-20/photon-main/tree/main)
## screenshot of the main window
## this project was done in the Software Engineering Class SPRING 2026 at UNIVERSITY OF ARKANASAS
<img width="1476" height="827" alt="Screenshot 2026-04-22 at 1 06 49 PM" src="https://github.com/user-attachments/assets/c46fd92e-623e-4898-8486-7278821793dd" />


## Quick Run Instructions (Linux)
## Install script has two versions based on your native OS —Mac and Windows. Please use the version appropriate for your system:
Both install scripts are for a Debian Linux environment. If you are using a Virtual Machine (Debian Linux) on a Mac, please use the _macinstall.sh_ script. If you are either using a Virtual Machine (Debian Linux) on Windows _or_ just using a native Debian Linux machine, please use the _wininstall.sh_.

**TLDR: For Debian Linux or Windows(using Linux VM).**
 
1. Fix line endings
```
sed -i 's/\r$//' ./wininstall.sh run.sh
```

2. Make scripts executable:
```
chmod +x wininstall.sh run.sh
```

3. Install software:
```
./wininstall.sh
```

4. Launch main program:
```
./run.sh
```

**TLDR: For a Mac(using Linux VM).**

1. Fix line endings
```
sed -i 's/\r$//' ./macinstall.sh run.sh
```

2. Make scripts executable:
```
chmod +x macinstall.sh run.sh
```

3. Install software:
```
./macinstall.sh
```

4. Launch main program:
```
./run.sh
```



## File organization

<table>
<thread>
 <tr>
  <th>folder</th><th>includes</th>
 </tr>
</thread>
<tr>
 <td>assets</td><td>images and sound used in App</td>
</tr>
<tr>
 <td>config</td><td>structured info outside the control of this repo</td>
</tr>
<tr>
 <td>doc</td><td>documentations and references</td>
</tr>
<tr>
 <td>src</td><td>source files (.py)</td>
</tr>
</table>

## TODOs (Sprint 4)
by April 19th
- [x] implement UDP server logic, run game using traffic_generator.py (Ali)
- [x] update score in scoreboard on socket recvfrom() (Thomas)
- [x] add base icon to player hitting base in scoreboard (Ryoji)
- [x] implement friendly fire logic (Ryoji)
- [x] add random music throughout game action (Wahid)
- [x] clean up UI and debug existing minor faults (Thomas and Ryoji)



## Tech stacks
- Python
- PyQt6
- Postgre Sequel
- UDP Sockets

## GitHub Contributors
- aliibek : Mukhammadali Madaminov
- wahid123542: Wahid Sultani
- thoma-sH : Thomas Hamilton
- TrueRyoB : Ryoji Araki
