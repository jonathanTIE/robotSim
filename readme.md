

# Utilisation :

Pour mettre à jour le fichier lua unique, utiliser amalgamage.py :

	& C:/Users/Jonathan/anaconda3/envs/robot_sim/python.exe d:/Sync/Code/Robotique/CDR2024/robotSim/lua_scripts/amalgamage.py D:/Sync/Code/Robotique/CDR2024/robotSim/lua_scripts/main2.lua

## Installation :

Installer eCAL

TODO : requirements.txt
PYTHON : Nécessite eCAL, protobuf, matplotlib, (flask), pysimplegui

## Usage

# Compilation

## Si besoin de mettre à jour "l'API" du robot / protobuf

Récupérer le dernier fichier `game_actions.h` depuis [felixzero/escrocs/actions/](https://github.com/felixzero/escrocs/blob/master/code/main_board/src/actions/game_actions.h)

(Linux) Compiler le projet pour executer protogen.cpp (TODO : Le projet ne se compile pas s'il manque game_actions.proto, éviter de le supprimer en workaround)

(Windows) Executer protogen.exe

-> game_actions.proto est regénéré
-> les pb.h sont générés lors de la compilation du projet (=runner.cpp)

Pour générer les pb2.py (Python):

Depuis /robotSim :

	protoc --python_out=./gui ./proto/game_actions.proto

# TODO

- Implémenter un "hot reload" du script lua. (envoyer un msg sur lua_path_loader supprime le lua_state actuel et en crée un nouveau)



