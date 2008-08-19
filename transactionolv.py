"""
A refactor of TransactionGrid, using ObjectListView.

Can we bind this to the list so inserts and removals and automatically handled?

IMPLEMENTED:
- displaying transactions
- editable amounts/descriptions
- edits pushed to model
TODO (for feature parity):
- editable date
- total based on total of last transaction
- totals automatically updates for transaction changes above them
- display negative amount as Red
- right-click context menu
  - remove
  - calculator options on amounts
- handle new transactions
EXTRA:
- custom negative option such as Red, (), or Red and ()

"""

import wx
from wx.lib.pubsub import Publisher
from ObjectListView import GroupListView, ColumnDefn
from basemodel import float2str
from model_sqlite import Model


class TransactionOLV(GroupListView):
    def __init__(self, *args, **kwargs):
        GroupListView.__init__(self, *args, **kwargs)
        self.currentTotal = 0.0
        
        self.showGroups = False
        self.evenRowsBackColor = wx.Color(224,238,238)
        self.oddRowsBackColor = wx.WHITE
        self.cellEditMode = GroupListView.CELLEDIT_SINGLECLICK
        self.SetEmptyListMsg("No transactions entered.")
        self.SetColumns([
            ColumnDefn("Date", valueGetter="Date", minimumWidth=80),
            ColumnDefn("Description", valueGetter="Description", isSpaceFilling=True, minimumWidth=80),
            ColumnDefn("Amount", "right", valueGetter="Amount", stringConverter=float2str, minimumWidth=80),
            ColumnDefn("Total", "right", valueGetter=self.getTotal, stringConverter=float2str, minimumWidth=80, isEditable=False),
        ])
        
    def getTotal(self, transObj):
        #HACK!
        self.currentTotal += transObj.Amount
        return self.currentTotal
    

class olvFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.Size = (800, 600)
        panel = wx.Panel(self)
        self.Sizer = wx.BoxSizer()
        self.Sizer.Add(panel, 1, wx.EXPAND)
        panel.Sizer = wx.BoxSizer()

        m = Model('bank')
        transactions = m.getTransactionsFrom('Test')
        glv = TransactionOLV(panel, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        glv.SetObjects(transactions)

        panel.Sizer.Add(glv, 1, wx.EXPAND)
        Publisher.subscribe(self.onMessage)

    def onMessage(self, message):
        print message.topic, message.data


if __name__ == "__main__":
    app = wx.App(False)
    olvFrame(None).Show()
    app.MainLoop()