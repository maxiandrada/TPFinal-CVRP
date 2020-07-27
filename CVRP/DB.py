import sqlite3
from sqlite3 import Error

def create_connection(db_file):

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def DB():  
    database = r"baseDeDatos.db" 

    sql_sets_table = """CREATE TABLE IF NOT EXISTS Sets (
                        setId integer  PRIMARY KEY AUTOINCREMENT,
                        setName text NOT NULL
                        );"""

    sql_instancias_table =   """CREATE TABLE IF NOT EXISTS Instancias (
                                instanciaId integer PRIMARY KEY AUTOINCREMENT,
                                instanciaName text NOT NULL,
                                cantidadClientes integer NOT NULL,
                                nroVehiculos integer NOT NULL,
                                demanda text NOT NULL,
                                capacidad real NOT NULL,
                                optimoConocido real,
                                coordenadas text NOT NULL
                            );"""

    sql_resoluciones_table = """CREATE TABLE IF NOT EXISTS Resoluciones (
                                resolucionId integer PRIMARY KEY AUTOINCREMENT,
                                iteraciones integer NOT NULL,
                                optimoEncontrado real NOT NULL,
                                tenueADD integer NOT NULL,
                                tenureDROP integer NOT NULL,
                                porcentajeError real NOT NULL
                            );"""

    sql_instanciasXset_table =   """CREATE TABLE IF NOT EXISTS InstanciasXSet (
                                    instanciaId integer NOT NULL,
                                    setId integer NOT NULL,
                                    PRIMARY KEY(instanciaId,setId),
                                    FOREIGN KEY (instanciaId) REFERENCES Instancia (instanciaId),
                                    FOREIGN KEY (setId) REFERENCES Sets (setId)
                                );"""

    sql_resolucionesXinstancia_table =   """CREATE TABLE IF NOT EXISTS resolucionesXInstancia (
                                            resolucionId integer NOT NULL,
                                            setId integer NOT NULL,
                                            PRIMARY KEY(setId,resolucionId),
                                            FOREIGN KEY (resolucionId) REFERENCES Resoluciones (resolucionId),
                                            FOREIGN KEY (setId) REFERENCES Sets (setId)
                                        );"""



    # crear conexión con base de datos
    conn = create_connection(database)

    # create tables
    if conn is not None:
        create_table(conn, sql_sets_table)
        create_table(conn, sql_instancias_table)
        create_table(conn, sql_resoluciones_table)
        create_table(conn, sql_resolucionesXinstancia_table)
        create_table(conn, sql_instanciasXset_table)
    else:
        print("Error no se puede conectar a la base de datos")

    return conn
def create_table(conn, create_table_sql):

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_set(conn,_set):
    sql = ''' INSERT INTO Sets (setName) VALUES (?) '''
    
    cur = conn.cursor()
    cur.execute(sql, _set)
    conn.commit()

    return cur.lastrowid

def insert_resolucion(conn,resolucion):
    sql = ''' INSERT INTO Resoluciones (iteraciones,optimoEncontrado,tenueADD,tenureDROP,porcentajeError) VALUES (?,?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(sql, resolucion)
    conn.commit()

    return cur.lastrowid
 
def insert_resolucionXInstancia(conn, resXinst):
    sql = ''' INSERT INTO ResolucionesXInstancia (resolucionId,instanciaId) VALUES (?,?) '''
    cur = conn.cursor()
    cur.execute(sql, resXinst)
    conn.commit()
    return cur.lastrowid


def insert_instancia(conn,instancia):
    sql = ''' INSERT INTO Instancias (instanciaName,cantidadClientes,nroVehiculos,demanda,capacidad,optimoConocido,coordenadas) VALUES (?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, instancia)
    conn.commit()

    return cur.lastrowid


def insert_instanciaXSet(conn,InstanciaXSet):
    sql = ''' INSERT INTO InstanciasXSet (instanciaId,setId) VALUES (?,?) '''
    cur = conn.cursor()
    cur.execute(sql, InstanciaXSet)
    conn.commit()

    return cur.lastrowid

def select_instancia(conn,instanciaId):
    sql =   f'''select * 
                from Instancias  
                WHERE instanciaId = {instanciaId}'''
    cur = conn.cursor()
    cur.execute(sql)
    filas = cur.fetchall()
    return filas

def select_instanciaXSet(conn,setId):
    sql =   f'''select Instancias.instanciaId,instanciaName,cantidadClientes,nroVehiculos,capacidad,optimoConocido 
                from Instancias INNER  JOIN InstanciasXSet ON InstanciasXSet.instanciaId = Instancias.instanciaId 
                WHERE setId = {setId}'''
    cur = conn.cursor()
    cur.execute(sql)
    filas = cur.fetchall()
    return filas

def select_sets(conn):
    sql = """select * from Sets """
    cur = conn.cursor()
    cur.execute(sql)
    filas = cur.fetchall()
    return filas
if __name__ == '__main__':
    DB()
    