import argparse
from neo4j import GraphDatabase


# start neo4j driver

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'neo4j'))

# functions

def run(query):
    """
    run a Neo4j query in Cypher

    parameters:
        query : Cypher-like query
        driver : neo4j driver
    
    return
        neo4j_response : JSON file with elements in the RETURN Cypher query
    """
    with driver.session() as session:
        neo4j_response = session.run(query).data()
    
    return neo4j_response


def parse_coordinates():
    """
    parse coordinates from the command line
    
    parameters:
        None
    
    return
        args : coordinates p1_x, p1_y, p2_x, p2_y
    """
    parser = argparse.ArgumentParser(description='Collect coordinates.')

    parser.add_argument('p1_x',type=float, nargs='+',help='Enter x for p1')
    parser.add_argument('p1_y',type=float, nargs='+',help='Enter y for p1')
    parser.add_argument('p2_x',type=float, nargs='+',help='Enter x for p2')
    parser.add_argument('p2_y',type=float, nargs='+',help='Enter y for p2')

    args = parser.parse_args()
    return args


def create_temp_point(name, x, y):
    """create a temporary point in the graph"""
    query = f"""CREATE (p:Temp {{name : '{name}', x: toFloat({x}), y: toFloat({y})}})"""
    run(query)


def create_temp_relationship(name):
    """create temporary relationship between point and the closest station"""
    query = f"""
    MATCH (s:Station), (p:Temp {{name:'{name}'}})
    WITH s, p, sqrt((s.x-p.x)^2+(s.y-p.y)^2) / 1000 AS distance_km ORDER BY distance_km LIMIT 1
    CREATE (p)-[r1:TEMP]->(s) 
    SET r1.time_m = distance_km *60/4
    CREATE (p)<-[r2:TEMP]-(s) 
    SET r2.time_m = distance_km *60/4
    RETURN s
    """
    run(query)


def shortest_path(start, stop):
    """find the shortest path between start and stop"""
    query = f"""
    MATCH (s1:Temp {{name: '{start}'}})
    MATCH (s2:Temp {{name: '{stop}'}})
    CALL gds.alpha.shortestPath.stream({{
    nodeQuery: 'MATCH (n) RETURN id(n) as id',
    relationshipQuery: "MATCH (n1)-[r]-(n2) RETURN id(r) as id, id(n1) as source, id(n2) as target, r.time_m as cost",
    relationshipWeightProperty: 'cost',
    startNode: s1,
    endNode: s2
    }})
    YIELD nodeId, cost
    RETURN gds.util.asNode(nodeId), cost AS travel_time_minutes
    """
    result = run(query)
    return result


def display_route(path):
    """
    display route with name of stations, line and time to get there
    """
    for node in path:
        if node['gds.util.asNode(nodeId)']['name'] == 'START':
            print('DEPART')
        elif node['gds.util.asNode(nodeId)']['name'] == 'STOP':
            print("POINT DE RDV dans ", round(node['travel_time_minutes'],2), "min")
        else:
            print(f"{node['gds.util.asNode(nodeId)']['name']: <25} Ligne {node['gds.util.asNode(nodeId)']['line']: <5} Arrivée dans {round(node['travel_time_minutes'],2)}min")


def remove_temp_item():
    """ remove all element with :Temp label"""
    run("""MATCH (n:Temp) DETACH DELETE n""")


def main():
    
    # catch coordinates from the command line
    args = parse_coordinates()
    x_start = float(args.p1_x[0])
    y_start = float(args.p1_y[0])
    x_stop = float(args.p1_x[0])
    y_stop = float(args.p2_y[0])

    # create temporary start_point<>start_station and stop_station<>stop_point relationships
    create_temp_point('START',x_start,y_start)
    create_temp_relationship('START')
    create_temp_point('STOP',x_stop,y_stop)
    create_temp_relationship('STOP')

    # find best route and display it
    sp = shortest_path('START', 'STOP')
    print(sp)
    display_route(sp)

    # remove temp nodes and relationship
    remove_temp_item()


if __name__ == "__main__":
    main()