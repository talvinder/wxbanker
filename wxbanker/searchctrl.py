#    https://launchpad.net/wxbanker
#    searchctrl.py: Copyright 2007-2009 Mike Rooney <mrooney@ubuntu.com>
#
#    This file is part of wxBanker.
#
#    wxBanker is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wxBanker is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with wxBanker.  If not, see <http://www.gnu.org/licenses/>.

import wx
from wxbanker import bankcontrols
from wx.lib.pubsub import Publisher


class SearchCtrl(wx.Panel):
    def __init__(self, parent, bankController):
        wx.Panel.__init__(self, parent)
        self.bankController = bankController

        self.searchCtrl = wx.SearchCtrl(self, value="", size=(200, -1), style=wx.TE_PROCESS_ENTER)
        # Try to grab the GTK system icon for clearing a search, otherwise we'll get the wxPython one.
        clearBitmap = wx.ArtProvider.GetBitmap('edit-clear')
        if clearBitmap:
            self.searchCtrl.SetCancelBitmap(clearBitmap)
        self.searchCtrl.ShowCancelButton(True)
        self.searchCtrl.ShowSearchButton(False)
        self.searchCtrl.DescriptiveText = _("Search transactions")

        # The More/Less button.
        self.moreButton = bankcontrols.MultiStateButton(self, labelDict={True: _("More options"), False: _("Less options")}, state=True)

        self.matchChoices = [_("Amount"), _("Description"), _("Date")]
        self.matchBox = bankcontrols.CompactableComboBox(self, value=self.matchChoices[1], choices=self.matchChoices, style=wx.CB_READONLY)

        self.caseCheck = wx.CheckBox(self, label=_("Case Sensitive"))
        self.caseCheck.SetToolTipString(_("Whether or not to match based on capitalization"))

        topSizer = wx.BoxSizer()
        topSizer.Add(self.searchCtrl, 0, wx.ALIGN_CENTER_VERTICAL)
        topSizer.AddSpacer(10)
        topSizer.Add(self.moreButton, 0, wx.ALIGN_CENTER_VERTICAL)

        self.moreSizer = moreSizer = wx.BoxSizer()
        moreSizer.Add(wx.StaticText(self, label=_("Match: ")), 0, wx.ALIGN_CENTER_VERTICAL)
        moreSizer.Add(self.matchBox, 0, wx.ALIGN_CENTER_VERTICAL)
        moreSizer.AddSpacer(5)
        moreSizer.Add(self.caseCheck, 0, wx.ALIGN_CENTER_VERTICAL)

        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(topSizer, 0, wx.ALIGN_CENTER)
        self.Sizer.Add(moreSizer, 0, wx.ALIGN_CENTER)
        self.matchBox.Compact()
        self.Layout()

        self.searchCtrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.onCancel)
        #self.searchCtrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.onSearch)
        self.searchCtrl.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
        self.moreButton.Bind(wx.EVT_BUTTON, self.onToggleMore)
        # Bindings to search on settings change automatically.
        self.matchBox.Bind(wx.EVT_COMBOBOX, self.onSearchTrigger)
        self.caseCheck.Bind(wx.EVT_CHECKBOX, self.onSearchTrigger)

        # Initially hide the extra search options.
        self.onToggleMore()

    def onSearchTrigger(self, event):
        event.Skip()
        self.onSearch()

    def onSearch(self, event=None):
        # TODO: enable search button in ctrl and appropriate event handling
        searchString = self.searchCtrl.Value # For a date, should be YYYY-MM-DD.
        matchType = self.matchChoices.index(self.matchBox.Value)
        caseSens = self.caseCheck.Value

        searchInfo = (searchString, matchType, caseSens)
        Publisher().sendMessage("SEARCH.INITIATED", searchInfo)

    def onCancel(self, event):
        self.searchCtrl.Value = ""
        Publisher().sendMessage("SEARCH.CANCELLED")
        #event.Skip()

    def onToggleMore(self, event=None):
        # Show or hide the advanced search options.
        showLess = self.Sizer.IsShown(self.moreSizer)
        self.Sizer.Show(self.moreSizer, not showLess)

        # Update appropriate strings, and make them fully translatable.
        self.moreButton.State = showLess
        if showLess:
            tipActionStr = _("Show advanced search options")
        else:
            tipActionStr = _("Hide advanced search options")
        self.moreButton.SetToolTipString(tipActionStr)

        # Give or take the appropriate amount of space.
        self.Parent.Layout()
        Publisher().sendMessage("SEARCH.MORETOGGLED")