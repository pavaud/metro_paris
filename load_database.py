from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4j"))


def run(query):
    with driver.session() as session:
        session.run(query).data()


print("\nSTART DATABASE CREATION\n")

# create database
print("Inserting Nodes and Relationships")
queries = [
    """// delete previous data
    MATCH (n)
    DETACH DELETE n
    """,
    """// inserting Nodes
    LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/pauldechorgnat/cool-datasets/master/ratp/stations.csv' AS row
    CREATE (:Station {
    name_clean: row.nom_clean,
    name:row.nom_gare,
    x: toFloat(row.x),
    y: toFloat(row.y),
    trafic_avg: toInteger(row.Trafic),
    city:row.Ville,
    line:row.ligne});
    """,
    """// Metro monnections
    LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/pauldechorgnat/cool-datasets/master/ratp/liaisons.csv' AS row
    MATCH (s1:Station) WHERE s1.name_clean = row.start AND s1.line = row.ligne
    MATCH (s2:Station) WHERE s2.name_clean = row.stop AND s2.line = row.ligne
    CREATE (s1)-[:METRO {name:s1.name_clean+'_to_'+s2.name_clean+'_line_'+row.ligne,
    distance_km : sqrt((s1.x-s2.x)^2+(s1.y-s2.y)^2) / 1000,
    time_m: sqrt((s1.x-s2.x)^2+(s1.y-s2.y)^2) / 40000 * 60}]->(s2);
    """,
    """// Line changes
    MATCH (s1:Station),(s2:Station)
    WHERE (s1.name_clean = s2.name_clean) AND (s1.line<>s2.line)
    CREATE (s1)-[:CHANGE {name:s1.name_clean+'_change_'+s1.line+'_to_'+s2.line, time_m: 4}]->(s2);
    """,
    """// Walk connections
    MATCH (s1:Station),(s2:Station)
    WHERE (sqrt(abs(s1.x-s2.x)^2+abs(s1.y-s2.y)^2)/1000) < 1 AND (s1.name_clean<>s2.name_clean)
    CREATE (s1)-[:WALK {name:s1.name_clean+'_to_'+s2.name_clean+'_walking',
    distance_km : sqrt((s1.x-s2.x)^2+(s1.y-s2.y)^2) / 1000,
    time_m: sqrt((s1.x-s2.x)^2+(s1.y-s2.y)^2)*60/(4*1000)}]->(s2);
    """,
]

for q in queries:
    print(q)
    run(q)

print("END DATABASE CREATION")
