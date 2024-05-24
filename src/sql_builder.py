__doc__ = '''
Build SQL class for generating SQL Queries 
'''
import re
import sys
import logging as log

log.basicConfig(
        level=log.DEBUG,
        stream=sys.stdout,
       format='%(asctime)s - %(levelname)s - %(message)s'
)


class SqlBuilder():
    def __init__(self):
        self.statements = []


    def generate_query_operators(self, opper='and', parameters=None, override=False):
        log.info("")
        log.info("generate_query_operators - [%s][%s]", opper, parameters)
        params = []
        for param in parameters:
            if '=' in param:
                key, value = param.split("=")
                log.info("\t%s = %s", key, value)
                if ',' in value:
                    value = self._generate_in(value)
                    params.append(f"{opper.upper()} {key} IN {value}")
                else:
                    params.append(f"{opper.upper()} {key} = '{value}'")

            elif '~' in param:
                key, value = param.split("~")
                log.info("\t%s LIKE %s", key, value)
                params.append(f"{opper.upper()} {key} LIKE '%{value}%'")

            elif '^' in param:
                key, value = param.split("^")
                log.info("\t%s ^ %s", key, value)
                if ',' in value:
                    value = self._generate_in(value)
                    params.append(f"{opper.upper()} {key} NOT IN {value}")
                else:
                    params.append(f"{opper.upper()} {key} != '{value}'")

        log.info("")
        self.add_statements([{'name': opper, 'value': params}], override)


    @staticmethod
    def _generate_in(value):
        items = value.split(',')
        return " (" + ", ".join(f"'{item.strip()}'" for item in items) + ")"


    def get_statements(self):
        return self.statements


    @staticmethod
    def _value_to_arr(value):
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return value
        return value


    @staticmethod
    def remove_unused_parameters(query_obj):
        """Remove remaining blank parameters from the query:"""
        sql = re.sub(r'\{.*?\}', '', query_obj['value'])
        query_obj['value'] = sql
        return query_obj


    def add_statements_dict(self, new_statements):
        for key, value in new_statements.items():
            self.statements.append({'name': key, 'value': [value]})


    def add_statements(self, new_statements, override=False):
        log.info("add_statements\toverride?[%s][%s]", override, new_statements)
        for new_statement in new_statements:
            statement_found = False
            for statement in self.statements:
                if 'name' in statement:
                    # Override existing statements
                    if override and statement['name'] == new_statement['name']:
                        statement['value'] = new_statement['value']
                        statement_found = True
                    # Append the statements if name matches
                    elif statement['name'] == new_statement['name']:
                        statement['value'] += new_statement['value']
                        statement_found = True
            # Add new statement if not found
            if not statement_found:
                self.statements.append(new_statement)

        return self.statements


    def update_sql_statement(self, query_obj):
        sql = query_obj['value']
        for param in self.statements:
            name = param['name']
            value = param['value']

            if isinstance(value, list):
                # Join list items with spaces
                value = ' '.join(value)

            # Replace the placeholder in the SQL query
            placeholder = f'{{{name}}}'
            sql = sql.replace(placeholder, value)

        query_obj['value'] = sql

        return query_obj
