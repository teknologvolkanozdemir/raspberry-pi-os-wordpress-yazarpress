"""Accessible GTK 3 desktop application for publishing to WordPress."""

import threading

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Atk", "1.0")
from gi.repository import Atk, GLib, Gtk

from wordpress import WordPressError, publish_content


class YazarPressWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="YazarPress — WordPress Yayıncısı")
        self.set_border_width(16)
        self.set_default_size(620, 560)
        self.set_resizable(True)

        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(layout)

        intro = Gtk.Label(
            label="WordPress sitenizde bir yazı veya sayfa yayınlayın."
        )
        intro.set_xalign(0)
        layout.pack_start(intro, False, False, 0)

        form = Gtk.Grid(column_spacing=12, row_spacing=10)
        layout.pack_start(form, False, False, 0)

        self.site_url = self._entry(form, 0, "_Web sitesi adresi", "https://ornek.com")
        self.username = self._entry(form, 1, "_Kullanıcı adı", "WordPress kullanıcı adı")
        self.password = self._entry(form, 2, "_Parola", "")
        self.password.set_visibility(False)
        self.password.set_input_purpose(Gtk.InputPurpose.PASSWORD)

        type_label = self._label("_Tür")
        self.content_type = Gtk.ComboBoxText()
        self.content_type.append("posts", "Yazı")
        self.content_type.append("pages", "Sayfa")
        self.content_type.set_active_id("posts")
        type_label.set_mnemonic_widget(self.content_type)
        form.attach(type_label, 0, 3, 1, 1)
        form.attach(self.content_type, 1, 3, 1, 1)

        guidance = Gtk.Label(
            label=(
                "WordPress uygulama parolası kullanın. Bilgileriniz yalnızca bu "
                "istek için kullanılır ve kaydedilmez."
            )
        )
        guidance.set_xalign(0)
        guidance.set_line_wrap(True)
        layout.pack_start(guidance, False, False, 0)

        self.title = self._entry(form, 4, "_Başlık", "İçerik başlığı")

        content_label = self._label("_İçerik")
        self.content_view = Gtk.TextView()
        self.content_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.content_view.set_accepts_tab(False)
        self.content_view.get_accessible().set_name("İçerik")
        self.content_view.get_accessible().set_description(
            "Yayınlanacak metni girin. Düzenleyiciden çıkmak için Sekme tuşuna basın."
        )
        content_label.set_mnemonic_widget(self.content_view)
        content_scroll = Gtk.ScrolledWindow()
        content_scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        content_scroll.set_min_content_height(180)
        content_scroll.add(self.content_view)
        form.attach(content_label, 0, 5, 1, 1)
        form.attach(content_scroll, 1, 5, 1, 1)
        form.set_hexpand(True)
        form.set_vexpand(True)
        content_scroll.set_vexpand(True)
        content_scroll.set_hexpand(True)

        self.publish_button = Gtk.Button.new_with_mnemonic("_Yayınla")
        self.publish_button.set_tooltip_text(
            "Seçilen yazı veya sayfayı WordPress'te yayınla."
        )
        self.publish_button.connect("clicked", self._publish)
        self.publish_button.set_can_default(True)
        self.set_default(self.publish_button)
        layout.pack_start(self.publish_button, False, False, 0)

        self.status = Gtk.Label(label="Hazır.")
        self.status.set_xalign(0)
        self.status.set_line_wrap(True)
        self.status.get_accessible().set_role(Atk.Role.STATUSBAR)
        layout.pack_start(self.status, False, False, 0)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    @staticmethod
    def _label(text):
        label = Gtk.Label.new_with_mnemonic(text)
        label.set_xalign(0)
        return label

    def _entry(self, form, row, label_text, placeholder):
        label = self._label(label_text)
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        label.set_mnemonic_widget(entry)
        form.attach(label, 0, row, 1, 1)
        form.attach(entry, 1, row, 1, 1)
        entry.set_hexpand(True)
        return entry

    def _publish(self, _button):
        buffer = self.content_view.get_buffer()
        content = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), True
        )
        values = (
            self.site_url.get_text(),
            self.username.get_text(),
            self.password.get_text(),
            self.content_type.get_active_id(),
            self.title.get_text(),
            content,
        )
        self.publish_button.set_sensitive(False)
        self.status.set_text("Yayınlanıyor…")
        threading.Thread(
            target=self._publish_in_background, args=(values,), daemon=True
        ).start()

    def _publish_in_background(self, values):
        try:
            result = publish_content(*values)
            title = result.get("title", {}).get("rendered", "İçerik")
            message = f"Başarıyla yayınlandı: {title}"
        except WordPressError as error:
            message = f"Yayınlama başarısız: {error}"
        except Exception:
            message = "Beklenmeyen bir hata nedeniyle yayınlama başarısız oldu."
        GLib.idle_add(self._finish_publish, message)

    def _finish_publish(self, message):
        self.status.set_text(message)
        self.publish_button.set_sensitive(True)
        return GLib.SOURCE_REMOVE


def main():
    YazarPressWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
