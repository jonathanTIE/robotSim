

# Utilisation :

## Installation :

Installer eCAL

TODO : requirements.txt
PYTHON : Nécessite eCAL, protobuf, matplotlib, flask

## Usage

Lancer `__simu_robot.py` . Paramètre par défaut : navigation différentielle.
Pour visualiser le robot sur matplotlib en temps réel, lancer `basic_plot.py`
Pour contrôler en vitesse, lancer `basic_teleop.py` et aller sur http://127.0.0.1:5000/
## Drivetrain (base roulante)

Pour la base roulante, les messages de commandes de vitesse correspondent pour le mode de navigation différentielle à vx, vy, vtheta.
Pour les robots holonomes 3 roues, vx = roue 1, vy = roue 2, vtheta = roue 3.

La roue 1 est celle avant, angle 0°, en haut. 
La roue 2 est celle à gauche, 120° par rapport à la roue 1.
La roue 3 est celle à droite, 120° par rapport à la roue 2. 
Secteur gauche : Entre roue 1 et roue 2
Secteur droit : entre roue 1 et 3
Secteur bas : entre roue 2 et 3.

Pour simplifier la programmation, la simulation n'avance que dans les directions où les roues pointent vers "l'extérieur" du robot (comme sur le schéma).
![](holonomic_robot.png)

Il pourrait être plus pertinent pour le vrai robot de faire avancer dans la direction inverse, pour que le robot fasse "chasse neige" d'obstacle au cas où.

# Compilation protobuf

## TODO/Warning :

Le game_actions.proto compilé par protogen n'est pas mis automatiquement dans ecal_lua/proto_messages

## reste des instructions 
Pour compiler les messages protobuf:

Récupérer le dernier fichier `game_actions.h` depuis https://github.com/felixzero/escrocs/blob/master/code/main_board/src/actions/game_actions.h
(Linux) Compiler ecal_lua
(Windows) Executer protogen.exe

Pour C++, il faut compiler tout ecal_lua pour ajouter les protobuf.
Pour Python :

Depuis /robotSim :
	protoc --python_out=./simulation --proto_path=**/PATH/TO** game_actions.proto

Pour Windows, le chemin devrait être ./out/build/x64-debug/ecal_lua/game_actions.proto
	protoc --python_out=./simulation --proto_path=./ecal_lua/out/build/x64-debug/ecal_lua game_actions.proto



