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
                sql = str(statement).strip(' \n;\t')
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

                      # if str(token).find(item.value) < str(token).find("FROM"):
                       if token.tokens[token.tokens.index(item)-2].value=="SELECT":

                          self._extract_select_clause(item)

                          self.preprocess_identifier(item)
                          '''
                          if self.tokenList[len(self.tokenList)-1]!="*":
                             self.tokenList.append("*")
                          '''


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
             if hasattr(item, 'get_alias'):
                 ExistsAlias = True
                 for Token in token.tokens[:token.tokens.index(item) - 1]:
                   if Token.value not in ALIAS and Token.value!="\n" :
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


if __name__ == '__main__':

    sql3="SELECT     /* LAS columns */  ls.ra, ls.dec,  ls.sourceID, ls.priOrSec, ls.frameSetID,  yapermag3, j_1apermag3, " \
         "hapermag3, kapermag3,  yapermag3err, j_1apermag3err, hapermag3err, kapermag3err,  yclass, j_1class, hclass, kclass, " \
         " yclassStat, j_1classStat, hclassStat, kclassStat  mergedclass, mergedclassStat,   pStar, pGalaxy, pNoise, pSaturated, " \
         " /* ErrBits */  ls.yErrBits, ls.j_1ErrBits, ls.hErrBits, ls.kErrBits,   ls.yppErrBits, ls.j_1ppErrBits, ls.hppErrBits," \
         " ls.kppErrBits,  /* x, y pixels  from detection tables*/ " \
         " ldy.x AS y_x, ldy.y AS y_y,  ldj.x AS j_x, ldj.y AS j_y,  ldh.x AS h_x, ldh.y AS h_y,  ldk.x AS k_x, ldk.y AS k_y, " \
         "  /* FIRST columns */  first.seqNo, first.ra AS ra_first, first.dec AS dec_first,  first.fint, first.fpeak, first.rms," \
         "  /* xmatch first columns */  LOF.distancemins as dr_first,   /* xmatch sdss columns */ " \
         " sdss.objid, LOS.distancemins as dr_sdss,  sdss.ra as ra_sdss, sdss.dec as dec_sdss,  sdss.psfmag_u, sdss.psfmag_g," \
         " sdss.psfmag_r,  sdss.psfmag_i, sdss.psfmag_z,  sdss.psfmagerr_u, sdss.psfmagerr_g, sdss.psfmagerr_r,  " \
         "sdss.psfmagerr_i, sdss.psfmagerr_z,  sdss.modelmag_u, sdss.modelmag_g, sdss.modelmag_r,  sdss.modelmag_i," \
         " sdss.modelmag_z,  sdss.modelmagerr_u, sdss.modelmagerr_g, sdss.modelmagerr_r,  sdss.modelmagerr_i, sdss.modelmagerr_z," \
         "  sdss.type, sdss.type_u, sdss.type_g,   sdss.type_r,sdss.type_i, sdss.type_z,  sdss.mode, sdss.flags, " \
         "  sdss.flags_u, sdss.flags_g, sdss.flags_r,   sdss.flags_i, sdss.flags_z,  /* SpecObj*/ Sso.z, Sso.zErr, Sso.zConf," \
         " Sso.zStatus, Sso.zWarning, Sso.specClass,  Sso.objTypeName  " \
         " /* INNER JOIN FIRST lasSourceXfirstSource with LasSource with */" \
         "  FROM    /* use the YJHK footprint */   LasYJHKSource AS ls " \
         " /* join conditions with mergelog table */  INNER JOIN Lasmergelog AS lml ON " \
         "    ls.framesetid = lml.framesetid    /* join conditions with source detection tables */ " \
         " INNER JOIN lasdetection AS ldy ON     ls.yseqnum = ldy.seqnum AND     lml.yenum = ldy.extNum AND  " \
         "   lml.ymfid = ldy.multiframeid   INNER JOIN lasdetection AS ldj ON     ls.j_1seqnum = ldj.seqnum " \
         " AND     lml.j_1enum = ldj.extNum AND     lml.j_1mfid = ldj.multiframeid    " \
         "  INNER JOIN lasdetection AS ldh ON     Lml.henum = Ldh.extNum AND" \
         "     lml.hmfid = Ldh.multiframeid and     ldh.seqnum = ls.hseqnum   " \
         "INNER JOIN lasdetection AS ldk ON     Lml.kenum = Ldk.extNum AND    " \
         " lml.kmfid = Ldk.multiframeid AND     ldk.seqnum = ls.kseqnum  INNER JOIN  " \
         "  /* Inner join between FIRST AND UKIDSS LAS */   (SELECT       sourceID, seqNo,      " \
         " masterObjID, slaveObjID, distancemins         FROM LasYJHKSource AS ls   " \
         " INNER JOIN LasSourceXfirstSource AS LxF       ON (LxF.masterObjID = ls.sourceID)  " \
         "  INNER JOIN FIRST..firstSource AS first       ON (LxF.slaveobjid = first.seqNo)    WHERE   " \
         "   /* resolved UKIDSS duplicate sources  */      ((ls.priOrSec = ls.frameSetID) OR (ls.priOrSec = 0)) AND    " \
         "  /* select within 1.5' */      (LxF.distanceMins < (1.5 / 60.0)) AND          LxF.distanceMins IN    " \
         "       /* select the nearest neighbour */     " \
         " (SELECT        MIN(distanceMins)      FROM      " \
         "  (SELECT              LXF.*            FROM              LasSourceXfirstSource AS LxF,          " \
         "    LasYJHKSource AS ls            WHERE              ((ls.priOrSec = ls.frameSetID) OR (ls.priOrSec = 0)) AND          " \
         "    LxF.masterObjID=ls.sourceID         ) AS LxF2      WHERE        LxF2.SlaveObjID=LxF.SlaveObjID)   ) AS LOF    ON  " \
         "    (ls.sourceid = LOF.sourceid)  INNER JOIN First..firstSource AS first    ON (first.seqNo = LOF.seqNo)  " \
         "  /* Left outer join with of UKIDSS with SDSS */ LEFT OUTER JOIN    (SELECT        sourceid, objid, distancemins  " \
         "   FROM       LasYJHKSource AS LS         INNER JOIN LasSourceXDR7PhotoObjAll AS LsXSp        " \
         "   ON LsXSp.masterObjID = Ls.sourceID         INNER JOIN BestDR7..PhotoObjAll AS Sp          " \
         " ON LsXSp.slaveobjid = Sp.objid     WHERE       /* set to 10.0 to decrease the drop out rate */  " \
         "     LsXSp.distanceMins<(10.0/60.0) AND       LsXSp.distanceMins IN        (SELECT MIN(T1.distanceMins) FROM             " \
         " LasSourceXDR7PhotoObj as T1            WHERE              T1.masterObjID = LsXSp.master"

    sql11="SELECT DISTINCT m.multiframeID, m.filterID, d.extnum FROM lasDetection s," \
          " Multiframe m, MultiframeDetector d WHERE s.ra between 207.25969522222223 and 207.26025077777777 and s.dec " \
          "between 11.919104122222224 and 11.919659677777778 and s.multiframeID = m.multiframeID  " \
          "and m.multiframeID = d.multiframeID  AND d.extnum=s.extnum "

    sql12="SELECT multiframeID FROM gpsDetection WHERE ra between 293.057 and 293.090" \
          " and dec between 12.923 and 12.956 /* Exclude multiple detections of the same source */AND ra > 0 "

    sql='select round( (K_1apermag3 - 1.36986*((Hapermag3-K_1apermag3)-0.03) + 1.62)*20,0)/20.0 as mu,count(*)' \
        ' as count FROM gpsJHKsource s WHERE s.l between      -7.75000 and   ' \
        '   -6.75000 and s.b between       4.85000 and       5.15000 and Hapermag3-K_1apermag3 ' \
        'between -1 and 6 and mergedClass != 0 and (PriOrSec=0 OR PriOrSec=framesetID) and K_1apermag3' \
        ' between 8 and 18 group by round( (K_1apermag3 - 1.36986*((Hapermag3-K_1apermag3)-0.03) + 1.62)*20,0)/20.0 '
    sql0='select s.sourceID, s.ra,s.dec,s.mergedClass,s.pStar,s.pGalaxy,s.pNoise,s.pSaturated, s.eBV,s.aJ,s.aH,s.aK, s.jclass,s.hclass,s.kclass, s.PriOrSec,s.jppErrbits,'\
' s.hppErrbits,s.kppErrbits, dj.AperMag1 as jAperMag1 ,dj.AperMag1Err as jAperMag1Err, dj.AperMag2 as jAperMag2 ,dj.AperMag2Err as jAperMag2Err,'\
' dj.AperMag3 as jAperMag3, dj.AperMag3Err as jAperMag3Err, dj.AperMag4 as jAperMag4 ,dj.AperMag4Err as jAperMag4Err, dj.AperMag5 as jAperMag5 ,'\
' dj.AperMag5Err as jAperMag5Err, dj.AperMag6 as jAperMag6, dj.AperMag6Err as jAperMag6Err, dj.AperMag7 as jAperMag7 ,dj.AperMag7Err as jAperMag7Err,'\
' dj.AperMag8 as jAperMag8 ,dj.AperMag8Err as jAperMag8Err, dj.AperMag9 as jAperMag9, dj.AperMag9Err as jAperMag9Err, dj.AperMag10 as jAperMag10 ,'\
' dj.AperMag10Err as jAperMag10Err, dj.AperMag11 as jAperMag11 ,dj.AperMag11Err as jAperMag11Err, dj.AperMag12 as jAperMag12, dj.AperMag12Err as '\
' jAperMag12Err, dj.AperMag13 as jAperMag13, dj.AperMag13Err as jAperMag13Err, dj.isoMag as jisoMag, dj.kronMag as jkronMag,dj.kronMagErr as jkronMagErr, '\
' dj.kronRad as jkronRad, dj.petroMag as jpetroMag, dj.petroMagErr as jpetroMagErr, dj.petroRad as jpetroMag, dj.psfMag as jpsfmag,dj.psfMagErr as jpefmagerr, '\
' dj.skyVar,dj.sky, mfdj.aperCorPeak as japercorpeack,mfdj.apercor1 as japercor1,mfdj.apercor2 as japercor2,mfdj.apercor3 as japercor3,mfdj.apercor4 as '\
' japercor4,mfdj.apercor5 as japercor5,mfdj.apercor6 as japercor6,mfdj.apercor7 as japercor7,mfdj.photZPcat as jphotzpcat,mfdj.photzperrcat as '\
' jphotzperrcat,mfdj.skyNoise as jskynoise,mfdj.seeing as jseeing,mfdj.coreRadius as jcoreradius,mfdj.TotalExpTime as jtotexptime,mfdj.extinctionCat as '\
 ' jextinctioncat, mfj.amstart as jamstart,1 as rel_flag from dxsSource as s join dxsMergeLog as ml on (s.framesetID=ml.framesetID)  left outer join '\
	' dxsDetection as dj on (dj.multiframeID=ml.jmfID and dj.extnum=ml.jenum and dj.seqNum=s.jSeqNum)  left outer join dxsDetection as dh on '\
	'  (dh.multiframeID=ml.hmfID and dh.extnum=ml.henum and dh.seqNum=s.hSeqNum)  left outer join dxsDetection as dk on (dk.multiframeID=ml.kmfID and '\
	'  dk.extnum=ml.kenum and dk.seqNum=s.kSeqNum)  join MultiframeDetector as mfdj on (mfdj.multiframeID=dj.multiframeID and mfdj.extnum=dj.extnum) '\
	 '   join MultiframeDetector as mfdh on (mfdh.multiframeID=dh.multiframeID and mfdh.extnum=dh.extnum)  join MultiframeDetector as mfdk on '\
	'   (mfdk.multiframeID=dk.multiframeID and mfdk.extnum=dk.extnum)  join Multiframe as mfk on (mfk.multiframeid = mfdk.multiframeid)  join '\
	 '     Multiframe as mfh on (mfh.multiframeid = mfdh.multiframeid)  join Multiframe as mfj on (mfj.multiframeid = mfdj.multiframeid) '\
	  '     where s.ra >= 157.4391667 and s.ra <= 166.01 and s.dec >= 55.75280556 and s.dec <= 60.296511 and s.PriOrSec = 0 and (s.jppErrbits = 0 or '\
	'      s.hppErrbits = 0 or s.kppErrbits = 0) union select s.sourceID, s.ra,s.dec,s.mergedClass,s.pStar,s.pGalaxy,s.pNoise,s.pSaturated, s.eBV,s.aJ,s.aH,s.aK, '\
	'	    s.jclass,s.hclass,s.kclass, s.PriOrSec,s.jppErrbits,s.hppErrbits,s.kppErrbits, dj.AperMag1 as jAperMag1 ,dj.AperMag1Err as jAperMag1Err, dj.AperMag2 as '\
	'	        jAperMag2 ,dj.AperMag2Err as jAperMag2Err, dj.AperMag3 as jAperMag3, dj.AperMag3Err as jAperMag3Err, dj.AperMag4 as jAperMag4 ,dj.AperMag4Err as jAperMag4Err, '\
	'		   dj.AperMag5 as jAperMag5 ,dj.AperMag5Err as jAperMag5Err, dj.AperMag6 as jAperMag6, dj.AperMag6Err as jAperMag6Err, dj.AperMag7 as jAperMag7 ,dj.AperMag7Err '\
		'   	        as jAperMag7Err, dj.AperMag8 as jAperMag8 ,dj.AperMag8Err as jAperMag8Err, dj.AperMag9 as jAperMag9, dj.AperMag9Err as jAperMag9Err, dj.AperMag10 as '\
			'		     jAperMag10 ,dj.AperMag10Err as jAperMag10Err, dj.AperMag11 as jAperMag11 ,dj.AperMag11Err as jAperMag11Err, dj.AperMag12 as jAperMag12, dj.AperMag12Err '\
					'	     		  as jAperMag12Err, dj.AperMag13 as jAperMag13, dj.AperMag13Err as jAperMag13Err, dj.isoMag as jisoMag, dj.kronMag as jkronMag,dj.kronMagErr as jkronMagErr, '\
' dj.kronRad as jkronRad, dj.petroMag as jpetroMag, dj.petroMagErr as jpetroMagErr, dj.petroRad as jpetroMag, dj.psfMag as jpsfmag,dj.psfMagErr as jpefmager,dj.skyVar,dj.sky, mfdj.aperCorPeak as japercorpeack,mfdj.apercor1 ' \
         'as japercor1,mfdj.apercor2 as japercor2,mfdj.apercor3 as japercor3,'
    sql4="SELECT   ROUND(RA, 6, 6) AS ra,  ROUND(Dec, 6, 6) AS dec,   ROUND(JAperMag3, 3, 3) AS mapp_j, " \
         " ROUND(JAperMag3Err, 3, 3) AS mapp_j_err,  ROUND(HAperMag3, 3, 3) AS mapp_h,  ROUND(HAperMag3Err, 3, 3) " \
         "AS mapp_h_err,  ROUND(KAperMag3, 3, 3) AS mapp_k,  ROUND(KAperMag3Err, 3, 3) AS mapp_k_err,  " \
         " ROUND(JClassStat, 3, 3) AS classstat_j,  ROUND(HClassStat, 3, 3) AS classstat_h,  ROUND(KClassStat, 3, 3) AS classstat_k, " \
         " ROUND(MergedClassStat, 3, 3) AS mergedclassstat,  MergedClass AS mergedclass,   PStar AS prob_star, " \
         " PGalaxy AS prob_galaxy,  PNoise AS prob_noise,  PSaturated AS prob_saturated  FROM   DXSSource  WHERE " \
         "  (30.0 <= RA) AND (RA <= 45.0) AND (-10.0 <= Dec) AND (Dec <= 0.0)  ORDER BY RA "
    sql5="SELECT (POWER(10.0,0.4*d.photZPCat)) as f0," \
         " ((1.0/m.expTime) * POWER(10.0, 0.4 * (aperCor3 - extinctionCat))) " \
         "as f_per_adu, d.photZPCat, d.photZPErrCat , d.extinctionCat, d.extinctionExt," \
         " d.aperCor3, d.skyCorrExt, d.skyCorrCat, d.totalExpTime, d.skyLevel, d.skyNoise, " \
         "m.extinction, m.expTime, m.amStart, m.amEnd FROM MultiframeDetector d, Multiframe m " \
         "WHERE d.multiframeID = m.multiframeID AND d.multiframeID = 986894 AND d.extnum = 4 " \
         "AND m.filterID=2 "
    sql6="SELECT distinct CAST( 'wget ''http://surveys.roe.ac.uk/wsa/cgi-bin/fits_download.cgi?file='+ REPLACE(REPLACE(fileName,'_two','')," \
         "'djoser:','')+''' -O '+ REPLACE(SUBSTRING(filename,CHARINDEX('/w2',fileName)+1,LEN(fileName)),'_two','') AS VARCHAR(256)) + " \
         "' # RABASE, DECBASE '+ cast(rabase as varchar(12))+', '+ cast(decbase as varchar(12))  FROM Multiframe as m, " \
         "gpsmergelog as g, currentastrometry as c  where g.hmfid=m.multiframeid /* H band matches */  " \
         "and m.multiframeid >0 and c.multiframeid=m.multiframeid and henum=c.extnum and (c.l > 357 or c.l < 60.5) "

    print("\n",SqlExtractor(sql3).tokens,"\n",len(SqlExtractor(sql3).tokens))#SqlExtractor(sql0).triple
    print(SqlExtractor(sql0).triple)
    SqlExtractor(sql11).sql

    
    
    
    data = np.array([])
    df = pd.read_csv('C:\\Users\\LiuJunshan\\Desktop\\homewoke\\AstroVec-main\\anonQCut.csv', engine='python')
    df = df.loc[df['dbname'].isin(['UKIDSSDR10PLUS', 'UKIDSSDR8PLUS', 'UKIDSSDR7PLUS'])]
    df = df.sample(n=200000)
    X_chosen, X_left = train_test_split(df.queryStr, random_state=42, test_size=0.4)
    a = 0
    for query in X_chosen:
             data = np.append(data,len(SqlExtractor(query).tokens))
    data_sorted = np.sort(data)
    p = 1. * np.arange(len(data)) / (len(data) - 1)
    fig = plt.figure()
    plt.plot(data_sorted, p)
    plt.xlabel('Query length in tokens')
    plt.ylabel('Proportion of queries')
    plt.title(u'CDF of Query Token Number')
    plt.show()
    OutPath='./'
    fig.savefig(OutPath + "cdf.png")




