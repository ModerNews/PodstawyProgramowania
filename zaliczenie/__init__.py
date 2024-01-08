import sys

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onButtonPressed(self, button):
        if button.get_label() == "button":
            print("Button clicked!")
            grid: Gtk.Grid = button.get_parent()
            grid.get_child_at(0, 3).set_property("active", True)

builder = Gtk.Builder()
builder.add_from_file("test.ui")
builder.connect_signals(Handler())

window = builder.get_object("MainWindow")
window.show_all()

Gtk.main()


# class MyApplication(Gtk.Application):
#     def __init__(self):
#         super().__init__(application_id="com.example.MyGtkApplication")
#         GLib.set_application_name('My Gtk Application')
#
#     def do_activate(self):
#         win = self.props.active_window
#         if not win:
#             win = StartWindow(application=self)
#         win.present()
#
#
# app = MyApplication()
# exit_status = app.run(sys.argv)
# sys.exit(exit_status)
