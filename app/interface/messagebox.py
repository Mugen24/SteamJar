from gi.repository import Gtk

def info(message, title=None, parent=None):

    if title is None:
        title = message[:16]

    dialog = Gtk.MessageDialog(
        transient_for = parent,
        flags = Gtk.DialogFlags.MODAL, 
        message_type = Gtk.MessageType.INFO,
        buttons = Gtk.ButtonsType.OK,
        title = title, 
        text = message
    )
    dialog.run()
    dialog.destroy()