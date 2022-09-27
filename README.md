# Metro à Paris

Ceci est un **TP d'évaluation** sur une base de donnés `neo4j`
- [Présentation](#présentation)
    - [Objectifs](#objectifs)
    - [Ressources](#Ressources)
    - [Création](#création)
    - [Requêtes](#requêtes)
    - [Application](#application)
- [Calculer un itinéraire](#calculer-un-itinéraire)
    - [Démarrer Neo4j](#démarrer-neo4j)
    - [Démarrer l'application](#démarrer-lapplication)


# Présentation

## Objectifs

> 1. **Création** : Créer une base de données `neo4j` des stations de métro de la ville de Paris.
> 2. **Requêtes** : Répondre à différentes questions sur la base en utilisant la syntaxe `Cypher`.
> 3. **Application** : Réaliser une application qui calcul l'itinéraire d'un point A à un point B dans Paris.

## Ressources

[`stations.csv`](data/stations.csv) : informations sur les stations
- `nom_clean` : nom de la station en majuscule
- `nom_gare` : nom de la station
- `x` : latitude en m
- `y` : longitude en m
- `Trafic` : le trafic estimé sur une année
- `Ville` : ville dans laquelle se trouve la station
- `ligne` : numéro de la ligne qui passe par la station

[`liaisons.csv`](data/liaisons.csv) : informations sur les liaisons entre stations
- `start` : station de début de la liaison
- `stop` : station de fin de la liaison
- `ligne` : ligne de la liaison

---

## Création
Le fichier [load_database.py](load_database.py) est un script python permettant de remplir la base `neo4j` avec :
-  `:Station` les stations de métro. Une stations est représentées **autant de fois** qu'il y a de lignes de métro qui passent par elle.

Ainsi que les différentes liaisons (bidirectionnelles) :
- `:METRO` laisons en métro
- `:CHANGE` correspondances à l'intérieur d'une station (entre 2 noeuds de la même station)
- `:WALK` liaison directement à pieds pour les distance inférieures à 1km

**Données approximées**:
- Temps moyen d'une correspondance : `4 min`
- Vitesse moyenne d'un métro : `40 km/h`

## Requêtes
Le fichier [exploration.cpy](exploration.cyp) contient des requêtes `Cypher` permettant de répondre aux différentes intérrogations suivantes

1. Quel est le nombre de correspondances par station ?
2. Quel est le nombre de stations à moins de deux kilomètres de la station `LADEFENSE` (on pourra prendre la distance brute sans considération de relation) ?
3. Combien de temps faut-il pour aller en metro de `LADEFENSE` à `CHATEAUDEVINCENNES` ?
4. Combien de temps faut-il pour aller à pied de `LADEFENSE` à `CHATEAUDEVINCENNES` (on pourra considérer que tout le chemin se fait à pied, sans considération de relation) ?
5. Est-il plus rapide de faire un changement à SAINTLAZARE pour aller de `MONTPARNASSEBIENVENUE` à `GABRIELPERI` ?
6. Combien de stations se trouvent dans un rayon de 10 stations par train autour de `STLAZARE` ?
7. Combien de stations se trouvent dans un rayon de 20 minutes par train autour de `STLAZARE` ?

## Application
Le fichier [route.py](route.py) contient l'application de calcul d'itinéraires.
L'application prend 4 paramètres:
- les coordonnées `x` et `y` des points de `départ` et d'`arrivée`

et elle renvoie les informations suivantes sur le meilleur itinéraire :
- les `stations` traversées
- les `lignes` de métro
- le `temps d'arrivée` à chaque station

**Algorithme utilisé** : [`shortest path`](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) de Dijkstra 

---

# Calculer un itinéraire

[revenir en haut](#metro-à-paris)

## Démarrer `Neo4j`

`Docker` doit être installé sur la machine.

1. Entrer la commande suivante dans un terminal `linux` ou `windows`
```bash
docker container run -p 7474:7474 -p 7687:7687 datascientest/neo4j
```
2. Se connecter ensuite depuis un **navigateur internet** à l’adresse :
    - `http://ip_machine_virtuelle:7474` si on passe par une machine virtuelle.
    - http://localhost:7474 en local.

La librairie `GraphDataScience` est chargée via l'image `Docker`, ce qui permet de faire des calcul de `plus court chemin` plus facilement.

## Démarrer l'application
Exécuter le script `route.py` avec deux points de coordonnées `x` et `y` en paramètres. Par ex:

```bash
python route.py 649417.3796 6862185.2617 656447.3488 6858608.5005
```