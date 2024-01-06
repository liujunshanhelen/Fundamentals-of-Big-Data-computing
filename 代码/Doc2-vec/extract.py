# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import pandas as pd
import numpy as np
import csv
import re
import string
import matplotlib.pyplot as plt
import sqlparse
from sklearn.model_selection import train_test_split
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import Keyword, Name, Comment
RESULT_OPERATIONS = {'UNION', 'INTERSECT', 'EXCEPT', 'SELECT'}
ON_KEYWORD = 'ON'
PRECEDES_TABLE_NAME = {'FROM', 'JOIN', 'DESC', 'DESCRIBE', 'WITH'}
ALIAS = {'AS','as'}
JOIN={'LEFT OUTER JOIN','ON','JOIN','join','OR','AND','UNION','SELECT',
      'WHERE','FROM','INNER JOIN','as','AS','table','with','conditions','MIN','MAX','min','max'}


class BaseExtractor(object):
    def __init__(self, sql_statement):
        self.tokenList = []
        self.triple={}
        self.sql = sqlparse.format(sql_statement, reindent=True, keyword_case='upper')
        self._Where_clauses = set()
        self._Select_clauses = set()

        self._Select_alias = set()
        self._table_names = set()
        self._alias_names = set()
        self._limit = None
        self._parsed = sqlparse.parse(self.stripped())

        for statement in self._parsed:

            self.__extract_token_to_lists(statement)
            self.__extract_from_token(statement)

            self._limit = self._extract_limit_from_query(statement)
        self._table_names = self._table_names - self._alias_names
        self.triple["select"] = self._Select_clauses
        self.triple["table"] = self._table_names
        self.triple["where"] = self._Where_clauses

    @property
    def tables(self):

        return self._table_names

    @property
    def whereClauses(self):

        return self._Where_clauses

    @property
    def SelectClauses(self):

        return self._Select_clauses



    @property
    def tablesAlias(self):

        return self._alias_names

    @property
    def tokens(self):
        return self.tokenList

    @property
    def Triple(self):

        return self.triple
    @property
    def limit(self):
        return self._limit

    def is_select(self):
        return self._parsed[0].get_type() == 'SELECT'

    def is_explain(self):
        return self.stripped().upper().startswith('EXPLAIN')

    def is_readonly(self):
        return self.is_select() or self.is_explain()

    def stripped(self):
        return self.sql.strip(' \t\n;')

    def get_statements(self):
        statements = []
        for statement in self._parsed:
            if statement:
                sql = str(statement).strip('\n;\t')
                if sql:
                    statements.append(sql)
        return statements

    @staticmethod
    def __precedes_table_name(token_value):
        for keyword in PRECEDES_TABLE_NAME:
            if keyword in token_value:
                return True
        return False

    @staticmethod
    def get_full_name(identifier):

        if len(identifier.tokens) > 1 and identifier.tokens[1].value == '.':
            return '{}.{}'.format(identifier.tokens[0].value,
                                  identifier.tokens[2].value)

        return identifier.get_real_name()

    @staticmethod
    def __is_result_operation(keyword):
        for operation in RESULT_OPERATIONS:
            if operation in keyword.upper():
                return True
        return False

    @staticmethod
    def __is_identifier(token):
        return isinstance(token, (IdentifierList, Identifier))

    def __process_identifier(self, identifier):

        if '(' not in '{}'.format(identifier):
            self._table_names.add(self.get_full_name(identifier))
            return
        # store aliases
        if hasattr(identifier, 'get_alias'):

            self._alias_names.add(identifier.get_alias())

        if hasattr(identifier, 'tokens'):
            # some aliases are not parsed properly

            if identifier.tokens[0].ttype == Name:
                self._alias_names.add(identifier.tokens[0].value)
        self.__extract_from_token(identifier)

    def as_create_table(self, table_name, overwrite=False):
        exec_sql = ''
        sql = self.stripped()
        if overwrite:
            exec_sql = 'DROP TABLE IF EXISTS {};\n'.format(table_name)
        exec_sql += 'CREATE TABLE {} AS \n{}'.format(table_name, sql)
        return exec_sql

    def __extract_token_to_lists(self, token):

        if not hasattr(token, 'tokens'):
            return
        table_name_preceding_token = False
        for item in token.tokens:
            if not item.is_group and item.ttype not in sqlparse.tokens.Whitespace and \
                    item.ttype not in sqlparse.tokens.Punctuation:
                # add:if condition for ahead attribute same name with dec...
                if str(token).find(item.value)<str(token).find("FROM") and item.ttype not in sqlparse.tokens.Keyword \
                        and item.ttype not in sqlparse.tokens.Wildcard:
                    item.ttype==None

                else:

                  self.tokenList.append(item.value)

            if item.is_group and not self.__is_identifier(item) and "WHERE" in item.value:
                self.__extract_from_childtoken(item)



            if item.is_group and self.__is_identifier(item):

                    if token.tokens.index(item)-2>=0:

                       if str(token).find(item.value) < str(token).find("FROM"):
                       #if token.tokens[token.tokens.index(item)-2].value=="SELECT":

                          self._extract_select_clause(item)
                          '''
                          self.preprocess_identifier(item)
                          '''
                          if self.tokenList[len(self.tokenList)-1]!="*":
                             self.tokenList.append("*")
                       else:
                           self.preprocess_identifier(item)
                    else:

                        self.preprocess_identifier(item)


    def preprocess_identifier(self, identifier):


       if (len(str(identifier).split())<=3):
           self.process_tokens(identifier)
       else:

         for item in identifier.tokens:
               if "select" in str(item).lower():#
                   if   str(item).endswith(")"):
                       sql_child=item.value[1:len(str(item))-2]
                   else:
                       sql_child = item.tokens[0].value[1:len(str(item)) - 2]

                   for item in SqlExtractor(sql_child).tokens:
                       self.tokenList.append(item)
               else:
                   self.process_tokens(item)


    def process_tokens(self, item):


        if item.ttype not in sqlparse.tokens.Punctuation \
                and item.ttype not in sqlparse.tokens.Whitespace and \
                item.ttype not in sqlparse.tokens.Wildcard:
            tokens = (re.sub(r'[^\w\s]', ' ', item.value)).split()

            if len(item.value.split()) == 1:
                if item.value.count(".") == 1:

                    self.tokenList.append(item.value[item.value.index(".") + 1:])
                else:

                    self.tokenList.append(item.value)
            else:

                self._extract_attribute(item)

    def _extract_attribute(self, token):

         pre_preserved =[]
         ExistsAlias=False
         if not hasattr(token, 'tokens'):
             return
         for item in token.tokens:
             #if item.value in ALIAS:
             '''
             if hasattr(item, 'get_alias'):
                 ExistsAlias = True
                 for Token in token.tokens[:token.tokens.index(item) - 1]:
                   if Token.value not in ALIAS and Token.value!="\n" :
                     pre_preserved.append(Token.value)
                 break
             '''
             if item.value in ALIAS:
                ExistsAlias=True
                for Token in  token.tokens[:token.tokens.index(item)-1]:
                    pre_preserved.append(Token.value)
                break
         if  ExistsAlias:

             dot_count=''.join(pre_preserved).count(".")
             preserved_list=''.join(pre_preserved).split()
             if len(preserved_list) == 1:
                 if dot_count == 1:
                     self.tokenList.append(''.join(pre_preserved)[''.join(pre_preserved).index(".") + 1:])

                 if dot_count == 2:

                     self.tokenList.append(''.join(pre_preserved))

                 if dot_count>2 or dot_count ==0:

                    self.tokenList.append( re.sub(r'[^\w\s]', '', ''.join(pre_preserved)).strip())
             else:

                for item in re.sub(r'[^\w\s]', ' ', ' '.join(pre_preserved)).split():
#maybe need modify
                   if item.isdigit() == False and ''.join(pre_preserved)[''.join(pre_preserved).find(item)+1]!="."  :
                      self.tokenList.append(item)


         else:

             if len(token.value.split()) == 2:
                 self.tokenList.append(token.tokens[0].value)
             else:
                 tokens = (re.sub(r'[^\w\s]', ' ', token.value)).split()
                 for item in tokens:
                     if item.isdigit() == False:
                         self.tokenList.append(item)


    def _extract_select_clause(self, token):


        if not hasattr(token, 'tokens'):
            return
        for item in token.tokens:
            if hasattr(item, 'get_alias'):
              self._Select_alias.add(item.get_alias())
            if isinstance(item, Identifier):
                attribute = item.value
                if "." in attribute:
                    attribute = attribute[attribute.index('.') + 1:]
                if attribute not in self._Select_clauses and len(attribute.split())==1 and attribute not in  self._Select_alias:
                    self._Select_clauses.add(attribute)
            if item.is_group:

                self._extract_select_clause(item)



    def __extract_from_childtoken(self, token):

        if not hasattr(token, 'tokens'):
            return
        for item in token.tokens:
            '''
            #dec are identified as built in in the sqlparse
            if item.value == 'dec':
                self.tokenList.append(item.value)

            if "select" in str(item).lower() and len(str(item).split())>1:  #
                if str(item).endswith(")"):
                    sql_child = item.value[1:len(str(item)) - 2]
                if not str(item).endswith(")") and not str(item).startswith("/*"):

                    sql_child = item.tokens[0].value[1:len(str(item)) - 2]
                    for items in SqlExtractor(sql_child).tokens:
                        self.tokenList.append(item)

            else:
            '''
            if item.ttype in Keyword:
                    self.tokenList.append(item.value)
            if isinstance(item, Identifier):
                    attribute = item.value
                    if "." in attribute:
                        attribute = attribute[attribute.index('.') + 1:]

                    self.tokenList.append(attribute)
                    if attribute not in self._Where_clauses:
                        self._Where_clauses.add(attribute)

            if item.is_group:
                    self.__extract_from_childtoken(item)

    def _extract_join_attribute(self,token):
       '''
         if 'WHERE'  in  token:
           token_part = token[token.index("WHERE") +1: ]
           self._extract_join_attribute(token_part)
       else:
          for item in token:
               if token.index(item) + 1 < len(token) \
                       and item not in JOIN :
                     if token[token.index(item) + 1] not in JOIN:
                        self._join_attributes.add(item)
                        self._join_attributes.add(token[token.index(item) + 1])


       '''


       self._join_attributes=self._Select_clauses&self._Where_clauses










    def __extract_from_token(self, token):
        if not hasattr(token, 'tokens'):
            return
        table_name_preceding_token = False
        for item in token.tokens:
            if item.ttype in Keyword:
                if self.__precedes_table_name(item.value.upper()):
                    table_name_preceding_token = True
                    continue
            if not table_name_preceding_token:
                continue
            if item.ttype in Keyword or item.value == ',':
                if (self.__is_result_operation(item.value) or
                        item.value.upper() == ON_KEYWORD):
                    table_name_preceding_token = False
                    continue

                break
            if isinstance(item, Identifier):
                self.__process_identifier(item)

            if isinstance(item, IdentifierList):
                for token in item.tokens:
                    if self.__is_identifier(token):
                        self.__process_identifier(token)
            if item.is_group and not self.__is_identifier(item):
                self.__extract_from_token(item)


    def _get_limit_from_token(self, token):
        if token.ttype == sqlparse.tokens.Literal.Number.Integer:
            return int(token.value)
        elif token.is_group:
            return int(token.get_token_at_offset(1).value)

    def _extract_limit_from_query(self, statement):

        limit_token = None
        for pos, item in enumerate(statement.tokens):
            if item.ttype in Keyword and item.value.lower() == 'limit':
                limit_token = statement.tokens[pos + 2]
                return self._get_limit_from_token(limit_token)

    def get_query_with_new_limit(self, new_limit):
        if not self._limit:
            return self.sql + ' LIMIT ' + str(new_limit)
        limit_pos = None
        tokens = self._parsed[0].tokens
        # Add all items to before_str until there is a limit
        for pos, item in enumerate(tokens):
            if item.ttype in Keyword and item.value.lower() == 'limit':
                limit_pos = pos
                break
        limit = tokens[limit_pos + 2]
        if limit.ttype == sqlparse.tokens.Literal.Number.Integer:
            tokens[limit_pos + 2].value = new_limit
        elif limit.is_group:
            tokens[limit_pos + 2].value = (
                '{}, {}'.format(next(limit.get_identifiers()), new_limit)
            )

        str_res = ''
        for i in tokens:
            str_res += str(i.value)
        return str_res


class SqlExtractor(BaseExtractor):
    """Extract sql statement"""

    @staticmethod
    def get_full_name(identifier, including_dbs=False):
        if len(identifier.tokens) > 1 and identifier.tokens[1].value == '.' and identifier.tokens[2].value == '.':
            a = identifier.tokens[0].value
            b = identifier.tokens[3].value
            db_table = (a, b)
            full_tree = '{}..{}'.format(a, b)

            return full_tree
        if len(identifier.tokens) > 1 and identifier.tokens[1].value == '.' and identifier.tokens[2].value != '.':
            a = identifier.tokens[0].value
            b = identifier.tokens[2].value
            db_table = (a, b)
            full_tree = '{}.{}'.format(a, b)
            if len(identifier.tokens) == 3:
                return full_tree
            else:
                i = identifier.tokens[3].value
                c = identifier.tokens[4].value
                if i == ' ':
                    return full_tree
                full_tree = '{}.{}.{}'.format(a, b, c)

                return full_tree
        if len(identifier.tokens) == 1:
            a = identifier.tokens[0].value
            full_tree = '{}'.format(a)

        if len(identifier.tokens) > 1 and identifier.tokens[1].value == ' ':
            a = identifier.tokens[0].value
            full_tree = '{}'.format(a)

        return full_tree


 
