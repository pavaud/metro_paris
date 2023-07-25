////////////////////////////////////////////////////////////////////////////////////
// Q1. Quel est le nombre de correspondances par station ?
MATCH (s1:Station)-[c:CHANGE]->()
RETURN s1.name, count(c); 

////////////////////////////////////////////////////////////////////////////////////
// Q2. Quel est le nombre de stations a moins de 2 km de la station LADEFENSE
// (on pourra prendre la distance brute sans consideration de relation) ?
MATCH (s1:Station {name_clean:'LADEFENSE'}),(s2:Station)
WITH s1, s2, (sqrt((s1.x-s2.x)^2+(s1.y-s2.y)^2)/1000) AS distance
WHERE (distance < 2) AND (s1.name_clean <> s2.name_clean)
RETURN count(s2) AS Nbr_stations_2km_chatelet;

// 2 Stations à moins de 2 km

////////////////////////////////////////////////////////////////////////////////////
// Q3. Combien de temps faut-il pour aller en metro de LADEFENSE à CHATEAUDEVINCENNES ?
MATCH (s1:Station {name_clean: 'LADEFENSE'})
MATCH (s2:Station {name_clean: 'CHATEAUDEVINCENNES'})
CALL gds.alpha.shortestPath.stream({
  nodeQuery: 'MATCH (n) RETURN id(n) as id',
  relationshipQuery: 'MATCH (n1)-[r:METRO]-(n2) RETURN id(r) as id, id(n1) as source, id(n2) as target, r.time_m as cost',
  relationshipWeightProperty: 'cost',
  startNode: s1,
  endNode: s2
})
YIELD cost
RETURN toInteger(round(cost)) AS travel_time_minutes
ORDER BY travel_time_minutes DESC
LIMIT 1

// 25 minute pour faire LADEFENSE à CHATEAUDEVINCENNES en métro

////////////////////////////////////////////////////////////////////////////////////
// Q4. Combien de temps faut-il pour aller à pied de LADEFENSE à CHATEAUDEVINCENNES
// (on pourra considà©rer que tout le chemin se fait à pied, sans considà©ration de relation) ?
MATCH (s1:Station {name_clean: 'LADEFENSE'})
MATCH (s2:Station {name_clean: 'CHATEAUDEVINCENNES'})
WITH s1,s2, sqrt((s1.x-s2.x)^2+(s1.y-s2.y)^2)*60/(4*1000) AS t
RETURN
  CASE
      WHEN t < 60 THEN toInteger(round(t)) +'min'
      ELSE toInteger(floor(t/60))+'h '+ toInteger(round((((t/60)-floor(t/60))*60))) + 'min'
  END
AS travel_time_walking

// 3h58 pour faire LADEFENSE à CHATEAUDEVINCENNES en marchant

////////////////////////////////////////////////////////////////////////////////////
// Q5. Est-il plus rapide de faire un changement à STLAZARE pour aller
// de MONTPARNASSEBIENVENUE à GABRIELPERI ?
MATCH (s1:Station {name_clean: 'MONTPARNASSEBIENVENUE'})
MATCH (s2:Station {name_clean: 'GABRIELPERI'})
CALL gds.alpha.shortestPath.stream({
  nodeQuery: 'MATCH (n) RETURN id(n) as id',
  relationshipQuery: "MATCH (n1)-[r]-(n2) RETURN id(r) as id, id(n1) as source, id(n2) as target, r.time_m as cost",
  relationshipWeightProperty: 'cost',
  startNode: s1,
  endNode: s2
})
YIELD nodeId, cost
RETURN gds.util.asNode(nodeId), cost AS travel_time_min

// On peut voir la succession des coûts dans l'onglet Text et on voit que :
// MONTPARNASSEBIENVENUE ligne 12 -> correspondance sur ligne 13 à STLAZARE -> GABRIELPERI ligne 13 : 18.42 min
// MONTPARNASSEBIENVENUE ligne 13 -> GABRIELPERI ligne 13 : 14.62 min
// Itinéraire plus rapide sans correspondance


////////////////////////////////////////////////////////////////////////////////////
// Q6. Combien de stations se trouvent dans un rayon de 10 stations par train autour
// de SAINTLAZARE ?
MATCH (s1:Station{name_clean:'STLAZARE'})
MATCH (s1)-[:METRO*1..10]-(s2)
WHERE s1.name_clean <> s2.name_clean
RETURN count(DISTINCT s2) as nb_rayon_10_stations;

//73 Stations sans changement dans un rayon de 10 Stations

////////////////////////////////////////////////////////////////////////////////////
// Q7. Combien de stations se trouvent dans un rayon de 20 minutes par train autour
// de STLAZARE ?
MATCH (s1:Station{name_clean:'STLAZARE'})
MATCH p=(s1)-[:METRO*]->(s2)
WHERE s1.name_clean <> s2.name_clean 
WITH p, s2, reduce(time=0, r IN relationships(p) | time + r.time_m) AS cost
WHERE cost < 20
RETURN count(DISTINCT s2) as nb_rayon_20min;

// 91 Stations dans un rayon de 20min