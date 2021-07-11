
import wx

class NumericTextfield(wx.TextCtrl):  
    def __init__(self, parent,*args,**kwargs):  
	if 'allowFloat' in kwargs:
		self.allowFloat=kwargs['allowFloat']#allowFloat
		del kwargs['allowFloat']
	else:
		self.allowFloat=True
	
        wx.TextCtrl.__init__(self, parent,*args,**kwargs)  
        wx.EVT_CHAR(self, self.OnChar)  
        

    def OnChar(self, event):  
        key = event.GetKeyCode()

        #print event.GetKey  
        if key > 47 and key < 58: #range for numbers  
            event.Skip()  
        elif key == 45: #minus symbol
	    event.Skip()
        #we allow only for one decimal point and only if we want a floatfield   
        elif key == 46 and self.allowFloat==True:   
            if '.' not in self.GetValue():  
                if self.GetInsertionPoint() != 0:  
                    event.Skip()  
        elif key == 8 or key == 127: #backspace and del  
            event.Skip()  
        elif key> 314 and key < 318: #cursor left up, right and down  
            event.Skip()  
        #print key

    #retrieve the value as float  
    def GetFloatValue(self):  
        return float(self.GetValue())

    #retrieve the value as int  
    def GetIntValue(self):  
        return int(float(self.GetValue()))