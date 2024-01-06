# Generated from C:\Users\LiuJunshan\Desktop\homewoke\Sql.g4 by ANTLR 4.7.2
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\b")
        buf.write("*\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\3\3\3\3\4\3\4\3\4\3\4\3")
        buf.write("\4\3\5\3\5\3\5\3\5\3\5\3\5\3\6\3\6\3\7\6\7\'\n\7\r\7\16")
        buf.write("\7(\2\2\b\3\3\5\4\7\5\t\6\13\7\r\b\3\2\3\4\2C\\c|\2*\2")
        buf.write("\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3")
        buf.write("\2\2\2\2\r\3\2\2\2\3\17\3\2\2\2\5\26\3\2\2\2\7\30\3\2")
        buf.write("\2\2\t\35\3\2\2\2\13#\3\2\2\2\r&\3\2\2\2\17\20\7U\2\2")
        buf.write("\20\21\7G\2\2\21\22\7N\2\2\22\23\7G\2\2\23\24\7E\2\2\24")
        buf.write("\25\7V\2\2\25\4\3\2\2\2\26\27\7,\2\2\27\6\3\2\2\2\30\31")
        buf.write("\7H\2\2\31\32\7T\2\2\32\33\7Q\2\2\33\34\7O\2\2\34\b\3")
        buf.write("\2\2\2\35\36\7Y\2\2\36\37\7J\2\2\37 \7G\2\2 !\7T\2\2!")
        buf.write("\"\7G\2\2\"\n\3\2\2\2#$\7?\2\2$\f\3\2\2\2%\'\t\2\2\2&")
        buf.write("%\3\2\2\2\'(\3\2\2\2(&\3\2\2\2()\3\2\2\2)\16\3\2\2\2\4")
        buf.write("\2(\2")
        return buf.getvalue()


class SqlLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    ID = 6

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'SELECT'", "'*'", "'FROM'", "'WHERE'", "'='" ]

    symbolicNames = [ "<INVALID>",
            "ID" ]

    ruleNames = [ "T__0", "T__1", "T__2", "T__3", "T__4", "ID" ]

    grammarFileName = "Sql.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


