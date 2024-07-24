from neo4j import GraphDatabase
from typing import List
from config.database import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class AccessControlManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.setup_schema()

    def close(self):
        self.driver.close()

    def setup_schema(self):
        with self.driver.session() as session:
            # Create unique constraints (acting as primary keys)
            session.run("CREATE CONSTRAINT user_name_unique IF NOT EXISTS FOR (u:User) REQUIRE u.name IS UNIQUE")
            session.run("CREATE CONSTRAINT group_name_unique IF NOT EXISTS FOR (g:Group) REQUIRE g.name IS UNIQUE")
            session.run("CREATE CONSTRAINT operation_name_unique IF NOT EXISTS FOR (o:Operation) REQUIRE o.name IS UNIQUE")
            session.run("CREATE CONSTRAINT permission_set_name_unique IF NOT EXISTS FOR (ps:PermissionSet) REQUIRE ps.name IS UNIQUE")

            # Create indexes
            session.run("CREATE INDEX user_name_index IF NOT EXISTS FOR (u:User) ON (u.name)")
            session.run("CREATE INDEX group_name_index IF NOT EXISTS FOR (g:Group) ON (g.name)")
            session.run("CREATE INDEX operation_name_index IF NOT EXISTS FOR (o:Operation) ON (o.name)")
            session.run("CREATE INDEX permission_set_name_index IF NOT EXISTS FOR (ps:PermissionSet) ON (ps.name)")

    def create_operation(self, operation_name: str):
        with self.driver.session() as session:
            session.run(
                """
                CREATE (:Operation {name: $name})
                """,
                name=operation_name
            )

    def create_permission_set(self, set_name: str, operations: List[str]):
        with self.driver.session() as session:
            session.run(
                """
                CREATE (ps:PermissionSet {name: $set_name})
                WITH ps
                UNWIND $operations as op
                MATCH (o:Operation {name: op})
                CREATE (ps)-[:INCLUDES]->(o)
                """,
                set_name=set_name,
                operations=operations
            )

    def create_group(self, group_name: str):
        with self.driver.session() as session:
            session.run(
                """
                CREATE (:Group {name: $name})
                """,
                name=group_name
            )

    def assign_permission_set_to_group(self, group_name: str, set_name: str):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (g:Group {name: $group_name})
                MATCH (ps:PermissionSet {name: $set_name})
                CREATE (g)-[:HAS_PERMISSION_SET]->(ps)
                """,
                group_name=group_name,
                set_name=set_name
            )

    def create_user(self, username: str):
        with self.driver.session() as session:
            session.run(
                """
                CREATE (:User {name: $name})
                """,
                name=username
            )

    def add_user_to_group(self, username: str, group_name: str):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {name: $username})
                MATCH (g:Group {name: $group_name})
                CREATE (u)-[:MEMBER_OF]->(g)
                """,
                username=username,
                group_name=group_name
            )

    def check_user_permission(self, username: str, operation: str) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {name: $username})-[:MEMBER_OF]->(g:Group)
                -[:HAS_PERMISSION_SET]->(ps:PermissionSet)
                -[:INCLUDES]->(o:Operation {name: $operation})
                RETURN COUNT(*) > 0 AS has_permission
                """,
                username=username,
                operation=operation
            )
            return result.single()["has_permission"]

    def get_user_permissions(self, username: str) -> List[str]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {name: $username})-[:MEMBER_OF]->(g:Group)
                -[:HAS_PERMISSION_SET]->(ps:PermissionSet)
                -[:INCLUDES]->(o:Operation)
                RETURN DISTINCT o.name AS operation
                """,
                username=username
            )
            return [record["operation"] for record in result]