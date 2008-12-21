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
- min column sizes when there aren't any transactions
EXTRA:
- custom negative option such as Red, (), or Red and ()

"""

import wx
from wx.lib.pubsub import Publisher
from ObjectListView import GroupListView, ColumnDefn
#from model_sqlite import Model
from banker import Bank # only temporary until Transactions can do float2str themselves


class TransactionOLV(GroupListView):
    def __init__(self, parent, bankController):
        GroupListView.__init__(self, parent, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        
        self.Model = bankController.Model
        
        self.showGroups = False
        self.evenRowsBackColor = wx.Color(224,238,238)
        self.oddRowsBackColor = wx.WHITE
        self.cellEditMode = GroupListView.CELLEDIT_SINGLECLICK
        self.SetEmptyListMsg("No transactions entered.")
        self.SetColumns([
            ColumnDefn("Date", valueGetter="Date"),
            ColumnDefn("Description", valueGetter="Description", isSpaceFilling=True),
            ColumnDefn("Amount", "right", valueGetter="Amount", stringConverter=self.Model.float2str),
            ColumnDefn("Total", "right", valueGetter=self.getTotal, stringConverter=self.Model.float2str, isEditable=False),
        ])
        
        self.Bind(wx.EVT_RIGHT_DOWN, self.onRightDown)
        
    def getTotal(self, transObj):
        """
        A somewhat hackish implementation, but an improvement!
        """
        i = self.GetIndexOf(transObj)
        if i == 0:
            total = transObj.Amount
        else:
            previousObj = self.GetObjectAt(i-1)
            try:
                previousTotal = previousObj._Total
            except AttributeError:
                previousTotal = self.getTotal(previousObj)
            
            total = previousTotal + transObj.Amount
                
        transObj._Total = total
        return total
    
    def setAccount(self, accountName, scrollToBottom=True):
        if accountName is None:
            transactions = []
        else:
            transactions = self.Model.GetAccount(accountName).Transactions
        
        self.Parent.Freeze()
        self.SetObjects(transactions)
        wx.CallLater(50, self.frozenResize) # Necessary for columns to size properly. (GTK)
        
        if scrollToBottom:
            self.ensureVisible(-1)
        
    def ensureVisible(self, index):
        if index < 0:
            index = self.GetItemCount() + index
        self.EnsureCellVisible(index, 0)
        
    def onRightDown(self, event):
        event.Skip()
        
    def frozenResize(self):
        self.Parent.Layout()
        self.Parent.Thaw()
    

class olvFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.Size = (800, 600)
        panel = wx.Panel(self)
        self.Sizer = wx.BoxSizer()
        self.Sizer.Add(panel, 1, wx.EXPAND)
        panel.Sizer = wx.BoxSizer()

        m = Model('bank')
        transactions = m.getTransactionsFrom('HSBC Checking')
        glv = TransactionOLV(panel)
        glv.SetObjects(transactions)

        panel.Sizer.Add(glv, 1, wx.EXPAND)
        Publisher.subscribe(self.onMessage)

    def onMessage(self, message):
        print message.topic, message.data


if __name__ == "__main__":
    app = wx.App(False)
    olvFrame(None).Show()
    app.MainLoop()
