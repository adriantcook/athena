# athena
query athena databases with dynamic stored SQL statements

## Configuration

### config:
There are only two configuration settings currently, default_database and s3_bucket.
```bash
default_database    - set the default database that athena will query,
                      you can override this in the query i.e. select * from database_name.table_name;

s3_bucket           - set the s3 bucket name where the results will be recored to
```


### values:
These are propagated into the parameters and parameters, you can use this to store static values that can be used in your queries and other parameters, this is handy if you keep calling the same static tables / or account_ids etc
I.e.
```json
values: [{
    "name": "my_aws_account_id",
    "value": "1234567890"
}],
parameters: [{
    "name": "aws_account_id",
    "value": "{my_aws_account_id}"
}],
queries: [
    "name": "query_account",
    value": "select * from my_table {my_aws_account_id};"
]
```


### parameters:
Parameters can be used for static values or queries
```json
parameters: [{
    "name": "aws_account_id",
    "value": "{my_aws_account_id}"
}],
```


## Queries
Write your stored queries here, you can then just call them by passing the name to the script, i.e. execute the `my_query_1` query:


```bash
$ athena -q 
```

```json
queries [
        {
            "name": "default",
            "value": "select * from my_table where 1 = 1 {and} {or} {like} {group_by} {order_by} {limit};"
        },
        {
            "name": "my_query_1",
            "value": "SELECT ROUND(SUM(line_item_blended_cost), 2) AS cost, year, month FROM {cost_report_table} WHERE 1 = 1 {year} {and} {or} {test} GROUP BY  year, month HAVING SUM(line_item_blended_cost) > 0 ORDER BY  cost DESC {limit};"
        }
]
```


## Stored parameters

The following stored parameters are used by the `athena` script as stored functions and will be called by the script, these be amended to the queries once added:
```json
{and}       - Additional AND statements
{or}        - Additional OR statements
{like}      - Additional LIKE statements

{group_by}  - Group by parameters
{order_by}  - Order by parameters

{limit}     - LIMIT BY X rows;
```

Add the above values in your query to be used: 
```sql
select * from my_table where 1 = 1 {and} {or} {like} {group_by} {order_by} {limit};
```

Use the above query, (-a) AND my_account_id=12341234 AND my_column=value2 OR (-o) my_column=value3, LIMIT 10 (-L 10)
```bash
$ athena -a my_account_id=12334234,my_column=value2 -o my_column=value3 -L 10
```

# Examples:

