

# Utilisation :

## Installation :

Installer eCAL

TODO : requirements.txt
PYTHON : Nécessite eCAL, protobuf, matplotlib, (flask)

## Usage

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



