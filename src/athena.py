__doc__ = '''
Athena class for querying athena database
'''
import sys
import logging as log
import boto3

from rich.console import Console
from rich.table import Table
from rich.style import Style

log.basicConfig(
        level=log.DEBUG,
        stream=sys.stdout,
       format='%(asctime)s - %(levelname)s - %(message)s'
)


class Athena():
    def __init__(self):
        pass


    def list_databases(self):
        client = boto3.client('athena')
        databases_response = client.list_databases(CatalogName='AwsDataCatalog')
        databases = databases_response['DatabaseList']

        for database in databases:
            db_name = database['Name']
            print(f"Database: {db_name}")
            tables_response = client.list_table_metadata(
                    CatalogName='AwsDataCatalog',
                    DatabaseName=db_name)
            tables = tables_response['TableMetadataList']

            for table in tables:
                table_name = table['Name']
                print(f"  Table: {table_name}")
            print("")


    def query(self, s3_bucket, database, query_obj):
        athena_client = boto3.client('athena')

        query = query_obj.get('value')

        query_execution = athena_client.start_query_execution(
            QueryExecutionContext={
                'Database': database,
            },
            QueryString=query,
            ResultConfiguration={
                'OutputLocation': s3_bucket,
            }
        )
        # Get the execution ID of your query
        execution_id = query_execution['QueryExecutionId']

        # Wait for the query to finish executing
        response = None
        query_status = None
        while query_status not in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            response = athena_client.get_query_execution(QueryExecutionId=execution_id)
            query_status = response['QueryExecution']['Status']['State']
            if query_status == 'FAILED':
                print("Query Failed!")
                print(response['QueryExecution']['Status']['StateChangeReason'])
                log.error(response)
                sys.exit(1)
            elif query_status == 'CANCELLED':
                print("Query Cancelled!")
                print(response['QueryExecution']['Status']['StateChangeReason'])
                log.error(response)
                sys.exit(1)

        # Once the query has finished, you can get the results
        if query_status == 'SUCCEEDED':
            response = athena_client.get_query_results(QueryExecutionId=execution_id)

        return {'query': query,
                'results': response,}


    def _extract_row_data(self, result):
        rows = result['ResultSet']['Rows']
        row_data = []
        for row in rows[1:]:  # Skip the first row as it contains column names
            row_values = []
            for value in row['Data']:
                if 'VarCharValue' in value:
                    row_values.append(value['VarCharValue'])
                else:
                    # or any default value you want to use for blank columns
                    row_values.append(None)
            row_data.append(row_values)
        return row_data


    def print_results(self, config, response, csv_mode=False):
        results = response.get('results')
        name = response.get('query')
        colors = config.get_colors()

        if results:
            if csv_mode:
                rows = self._extract_row_data(results)
                headers = [col['Label'] \
                        for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]

                print(','.join(headers))

                for row in rows:
                    print(",".join([val for val in row]))
            else:
                headers = [col['Label'] \
                        for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
                rows = self._extract_row_data(results)

                table = Table(title=name)
                row_styles = [Style(color=color) for color in colors]

                for column in headers:
                    table.add_column(column)

                for i, row in enumerate(rows):
                    row_style = row_styles[i % len(row_styles)]
                    table.add_row(*row, style=row_style)

                console = Console()
                console.print(table)
