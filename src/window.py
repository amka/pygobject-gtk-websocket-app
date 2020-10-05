# window.py
#
# Copyright 2020 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written
# authorization.

from gi.repository import Gtk, Soup


@Gtk.Template(resource_path='/com/github/tenderowl/spacebeam/window.ui')
class SpacebeamWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'SpacebeamWindow'

    overlay = Gtk.Template.Child()
    screens = Gtk.Template.Child()

    host_entry = Gtk.Template.Child()
    connect_btn = Gtk.Template.Child()
    disconnect_btn = Gtk.Template.Child()
    spinner = Gtk.Template.Child()

    send_btn = Gtk.Template.Child()
    message_entry = Gtk.Template.Child()
    log_view = Gtk.Template.Child()

    session = None
    connection = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.connect_btn.connect('clicked', self.on_connect_clicked)
        self.disconnect_btn.connect('clicked', self.on_disconnect_clicked)

        self.message_entry.connect('activate', self.on_send_clicked)
        self.send_btn.connect('clicked', self.on_send_clicked)
        self.buffer = self.log_view.get_buffer()

    def on_connect_clicked(self, widget):
        if not self.host_entry.get_text():
            self.host_entry.grab_focus()
            return

        self.spinner.start()

        self.session = Soup.Session()
        msg = Soup.Message.new("GET", self.host_entry.get_text())
        self.session.websocket_connect_async(msg, None, None, None, self.on_connection)

    def on_disconnect_clicked(self, widget):
        self.connection.close(1005)

        self.message_entry.set_text('')
        self.buffer.delete(self.buffer.get_start_iter(),
                           self.buffer.get_end_iter())

        self.disconnect_btn.set_visible(False)
        self.screens.set_visible_child_name('connection')

    def on_connection(self, session, result):
        try:
            self.connection = session.websocket_connect_finish(result)
            self.connection.connect('message', self.on_message)
            self.screens.set_visible_child_name('chat')
            self.disconnect_btn.set_visible(True)
        except Exception as e:
            print(e)
            self.session = None
        finally:
            self.spinner.stop()

    def on_message(self, connection, msg_type, message):
        msg = f'<b>RECEIVED:</b> {message.get_data().decode()}\n'
        self.buffer.insert_markup(self.buffer.get_start_iter(),
                                  msg,
                                  len(msg))

    def on_send_clicked(self, widget):
        msg = self.message_entry.get_text()
        if not msg or not self.connection:
            self.message_entry.grab_focus()
            return

        self.connection.send_text(msg)
        self.message_entry.set_text('')
        self.message_entry.grab_focus()


