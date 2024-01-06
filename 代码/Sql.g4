grammar Sql;

query: statement;

statement: 'SELECT' '*' 'FROM' table 'WHERE' expression;

table: ID;

expression: column '=' value;

column: ID;

value: ID;

ID: [a-zA-Z]+;