"""
PostgreSQL database connection using psycopg2
Alternative to Supabase for local development
"""
import psycopg2
import psycopg2.extras
import psycopg2.extensions
from typing import List, Dict, Any, Optional
import os
import json
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:12345@localhost:5432/skinguard")

# Register JSON adapter for dict types
psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)


class PostgreSQLClient:
    """Simple PostgreSQL client that mimics Supabase interface"""
    
    def __init__(self, database_url: str = DATABASE_URL):
        self.database_url = database_url
        self._conn = None
    
    def get_connection(self):
        """Get database connection"""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.database_url)
        return self._conn
    
    def table(self, table_name: str):
        """Return a table query builder"""
        return TableQuery(self, table_name)
    
    def rpc(self, function_name: str, params: dict = None):
        """
        Call a PostgreSQL function (RPC)
        Note: This is a simplified implementation that returns None
        For full RPC support, implement the specific function calls
        """
        # For now, return a result that will trigger fallback logic
        return QueryResult(None)
    
    def close(self):
        """Close database connection"""
        if self._conn and not self._conn.closed:
            self._conn.close()


class TableQuery:
    """Query builder for PostgreSQL tables"""
    
    def __init__(self, client: PostgreSQLClient, table_name: str):
        self.client = client
        self.table_name = table_name
        self._select_fields = "*"
        self._where_conditions = []
        self._where_values = []
        self._order_by = None
        self._limit_value = None
    
    def select(self, fields: str = "*"):
        """Select fields"""
        self._select_fields = fields
        return self
    
    def eq(self, column: str, value: Any):
        """Add WHERE column = value condition"""
        self._where_conditions.append(f"{column} = %s")
        self._where_values.append(value)
        return self
    
    def in_(self, column: str, values: List[Any]):
        """Add WHERE column IN (values) condition"""
        if not values:
            # Empty list - add condition that will never match
            self._where_conditions.append("1=0")
        else:
            placeholders = ', '.join(['%s'] * len(values))
            self._where_conditions.append(f"{column} IN ({placeholders})")
            self._where_values.extend(values)
        return self
    
    def order(self, column: str, desc: bool = False):
        """Add ORDER BY clause"""
        direction = "DESC" if desc else "ASC"
        self._order_by = f"{column} {direction}"
        return self
    
    def limit(self, count: int):
        """Add LIMIT clause"""
        self._limit_value = count
        return self
    
    def range(self, start: int, end: int):
        """Add LIMIT and OFFSET for pagination (Supabase-style range)"""
        self._limit_value = end - start + 1
        self._offset_value = start
        return self
    
    def insert(self, data: Dict[str, Any]):
        """Insert data into table"""
        self._insert_data = data
        return self
    
    def update(self, data: Dict[str, Any]):
        """Update data in table"""
        self._update_data = data
        return self
    
    def delete(self):
        """Delete from table"""
        self._is_delete = True
        return self
    
    def execute(self):
        """Execute the query"""
        conn = self.client.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # INSERT
            if hasattr(self, '_insert_data'):
                columns = list(self._insert_data.keys())
                values = list(self._insert_data.values())
                placeholders = ', '.join(['%s'] * len(values))
                query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *"
                cursor.execute(query, values)
                result = cursor.fetchall()
                conn.commit()
                return QueryResult([dict(row) for row in result])
            
            # UPDATE
            elif hasattr(self, '_update_data'):
                set_clause = ', '.join([f"{k} = %s" for k in self._update_data.keys()])
                values = list(self._update_data.values()) + self._where_values
                where_clause = ' AND '.join(self._where_conditions) if self._where_conditions else '1=1'
                query = f"UPDATE {self.table_name} SET {set_clause} WHERE {where_clause} RETURNING *"
                cursor.execute(query, values)
                result = cursor.fetchall()
                conn.commit()
                return QueryResult([dict(row) for row in result])
            
            # DELETE
            elif hasattr(self, '_is_delete'):
                where_clause = ' AND '.join(self._where_conditions) if self._where_conditions else '1=1'
                query = f"DELETE FROM {self.table_name} WHERE {where_clause}"
                cursor.execute(query, self._where_values)
                conn.commit()
                return QueryResult([])
            
            # SELECT
            else:
                where_clause = ' AND '.join(self._where_conditions) if self._where_conditions else '1=1'
                query = f"SELECT {self._select_fields} FROM {self.table_name} WHERE {where_clause}"
                
                if self._order_by:
                    query += f" ORDER BY {self._order_by}"
                if self._limit_value:
                    query += f" LIMIT {self._limit_value}"
                if hasattr(self, '_offset_value'):
                    query += f" OFFSET {self._offset_value}"
                
                cursor.execute(query, self._where_values)
                result = cursor.fetchall()
                return QueryResult([dict(row) for row in result])
        
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()


class QueryResult:
    """Query result wrapper"""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
    
    def __repr__(self):
        return f"QueryResult(data={self.data})"


# Global client instance
postgres_client = PostgreSQLClient()


def get_postgres_client() -> PostgreSQLClient:
    """Get PostgreSQL client instance"""
    return postgres_client
