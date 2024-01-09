import copy
import sys

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf, InterpType


class Filters:
    @staticmethod
    def PNG():
        filter = Gtk.FileFilter()
        filter.set_name("Obrazy PNG")
        filter.add_mime_type("image/png")
        filter.add_pattern("*.png")
        return filter

    @staticmethod
    def CSV():
        filter = Gtk.FileFilter()
        filter.set_name("Pliki CSV")
        filter.add_mime_type("text/csv")
        filter.add_pattern("*.csv")
        return filter

    @staticmethod
    def ANY():
        filter = Gtk.FileFilter()
        filter.set_name("Wszystkie pliki")
        filter.add_pattern("*")
        return filter


class ObjectCustomizer:
    def __init__(self, builder):
        self.builder = builder

    def instantiate_result_window(self):
        results = self.builder.get_object("ResultWindow")
        result_container: Gtk.Box = builder.get_object("result_container")
        # template_result: Gtk.Grid = builder.get_object("resultbox1")
        for i in range(100):
            new_result = Gtk.Grid()
            new_result.set_property("visible", True)
            new_result.set_property("can-focus", False)
            new_result.set_property("halign", Gtk.Align.CENTER)

            new_match_string = Gtk.Label()
            new_match_string.set_property("visible", True)
            new_match_string.set_property("can-focus", False)
            new_match_string.set_property("halign", Gtk.Align.START)
            new_match_string.set_property("label", "Twoja Stara")
            new_match_string.modify_font(Pango.font_description_from_string("JetBrainsMono Nerd Font 12"))

            new_match_file = Gtk.Label()
            new_match_file.set_property("visible", True)
            new_match_file.set_property("can-focus", False)
            new_match_file.set_property("halign", Gtk.Align.END)
            new_match_file.set_property("label", "Zapierdala")
            new_match_file.modify_font(Pango.font_description_from_string("JetBrainsMono Nerd Font Ultra-Light 10"))

            new_result.attach(new_match_string, 0, 0, 1, 1)
            new_result.attach(new_match_file, 1, 0, 1, 1)
            result_container.add(new_result)
        return results

    def instance_graph_dialog(self):
        graph: Gtk.Dialog = self.builder.get_object("GraphLookupDialog")

        desired_width = 640
        desired_height = 360

        pixbuf = Pixbuf.new_from_file('graph.png')
        pixbuf = pixbuf.scale_simple(desired_width, desired_height, InterpType.BILINEAR)
        builder.get_object("graphImage").set_from_pixbuf(pixbuf)
        graph.add_button("Zapisz", Gtk.ResponseType.OK)
        graph.add_button("Anuluj", Gtk.ResponseType.CANCEL)
        return graph


class Handler:
    def __init__(self, builder: Gtk.Builder):
        self.builder = builder
        self.object_builder = ObjectCustomizer(builder)

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onButtonPressed(self, grid: Gtk.Grid):
        print("Button clicked!")
        entry_text = self.builder.get_object("input_query").get_text()
        input_directory = self.builder.get_object("input_directory").get_current_folder()
        self.builder.get_object("processing_indicator_grid").set_property("visible", True)
        print(entry_text, input_directory)

        if entry_text == "" or input_directory is None:
            self.showErrorDialog("Nie podano wszystkich wymaganych danych!")
            return

        self.builder.add_from_file('results.ui')  # Add new from file to assert that contents of window aren't destroyed
        self.builder.connect_signals(self)
        result = self.object_builder.instantiate_result_window()
        result.show_all()

    def showErrorDialog(self, message: str):
        dialog = Gtk.MessageDialog(parent=self.builder.get_object("MainWindow"),
                                   modal=True,
                                   destroy_with_parent=True,
                                   message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.OK,
                                   icon_name="dialog-error",
                                   text=message)
        dialog.connect("response", self.errorDialogResponse)
        dialog.show()

    def errorDialogResponse(self, dialog: Gtk.MessageDialog, response: Gtk.ResponseType):
        self.builder.get_object("processing_indicator_grid").set_property("visible", False)
        dialog.close()

    def onGraphShowClicked(self, button: Gtk.Button):
        self.builder.add_from_file("graph_dialog.ui")
        self.builder.connect_signals(self)
        graph = self.object_builder.instance_graph_dialog()
        graph.connect("response", self.onGraphDialogResponse)
        graph.show()

    def onGraphDialogResponse(self, dialog: Gtk.Dialog, response: Gtk.ResponseType):
        if response == Gtk.ResponseType.OK:
            self.handle_graph_save()
        dialog.close()

    def handle_graph_save(self):
        graph_destination_dialog = Gtk.FileChooserDialog(title="Zapisz graf", action=Gtk.FileChooserAction.SAVE)
        graph_destination_dialog.set_current_folder(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES))
        graph_destination_dialog.set_current_name("graph.png")
        graph_destination_dialog.set_do_overwrite_confirmation(True)
        graph_destination_dialog.add_button("Zapisz", Gtk.ResponseType.OK)
        graph_destination_dialog.add_button("Anuluj", Gtk.ResponseType.CANCEL)
        graph_destination_dialog.add_filter(Filters.PNG())
        graph_destination_dialog.add_filter(Filters.ANY())
        graph_destination_dialog.connect("response", self.onSaveGraphDialogResponse)
        graph_destination_dialog.show()

    def onSaveResultsClicked(self, button: Gtk.Button):
        results_destination_dialog = Gtk.FileChooserDialog(title="Zapisz tabelę wyników",
                                                           action=Gtk.FileChooserAction.SAVE)
        results_destination_dialog.set_current_folder(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS))
        results_destination_dialog.set_current_name("matched_strings.csv")
        results_destination_dialog.set_do_overwrite_confirmation(True)
        results_destination_dialog.add_button("Zapisz", Gtk.ResponseType.OK)
        results_destination_dialog.add_button("Anuluj", Gtk.ResponseType.CANCEL)
        results_destination_dialog.add_filter(Filters.CSV())
        results_destination_dialog.add_filter(Filters.ANY())
        results_destination_dialog.connect("response", self.onSaveResultsDialogResponse)
        results_destination_dialog.show()

    def onSaveGraphDialogResponse(self, dialog: Gtk.FileChooserDialog, response: Gtk.ResponseType):
        if response == Gtk.ResponseType.OK:
            print("Saving graph to", dialog.get_filename())
            # TODO: Save graph
        dialog.close()

    def onSaveResultsDialogResponse(self, dialog: Gtk.FileChooserDialog, response: Gtk.ResponseType):
        if response == Gtk.ResponseType.OK:
            print("Saving results to", dialog.get_filename())
            dialog.close()
            # TODO: Save results
        elif response == Gtk.ResponseType.CANCEL:
            print("Results saving cancelled.")
            dialog.close()


builder = Gtk.Builder()
builder.add_from_file("test.ui")
handler = Handler(builder)
builder.connect_signals(handler)

window = builder.get_object("MainWindow")
# window.
window.show_all()
builder.get_object("processing_indicator_grid").set_property("visible",
                                                             False)  # Hide processing indicator, since template is visible by default
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
