# Generated from C:\Users\LiuJunshan\Desktop\homewoke\Sql.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SqlParser import SqlParser
else:
    from SqlParser import SqlParser

# This class defines a complete listener for a parse tree produced by SqlParser.
class SqlListener(ParseTreeListener):

    # Enter a parse tree produced by SqlParser#query.
    def enterQuery(self, ctx:SqlParser.QueryContext):
        pass

    # Exit a parse tree produced by SqlParser#query.
    def exitQuery(self, ctx:SqlParser.QueryContext):
        pass


    # Enter a parse tree produced by SqlParser#statement.
    def enterStatement(self, ctx:SqlParser.StatementContext):
        pass

    # Exit a parse tree produced by SqlParser#statement.
    def exitStatement(self, ctx:SqlParser.StatementContext):
        pass


    # Enter a parse tree produced by SqlParser#table.
    def enterTable(self, ctx:SqlParser.TableContext):
        pass

    # Exit a parse tree produced by SqlParser#table.
    def exitTable(self, ctx:SqlParser.TableContext):
        pass


    # Enter a parse tree produced by SqlParser#expression.
    def enterExpression(self, ctx:SqlParser.ExpressionContext):
        pass

    # Exit a parse tree produced by SqlParser#expression.
    def exitExpression(self, ctx:SqlParser.ExpressionContext):
        pass


    # Enter a parse tree produced by SqlParser#column.
    def enterColumn(self, ctx:SqlParser.ColumnContext):
        pass

    # Exit a parse tree produced by SqlParser#column.
    def exitColumn(self, ctx:SqlParser.ColumnContext):
        pass


    # Enter a parse tree produced by SqlParser#value.
    def enterValue(self, ctx:SqlParser.ValueContext):
        pass

    # Exit a parse tree produced by SqlParser#value.
    def exitValue(self, ctx:SqlParser.ValueContext):
        pass


