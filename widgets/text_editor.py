import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from widgets.auto_scrollbar import AutoScrollbar
from widgets.placeholder_entry import tkPlaceholderEntry
from widgets.custom_texts import CText, NumberedText



class TextEditor(ttk.Frame):
    def __init__(
        self,
        master,
        padding=0,
        bootstyle=DEFAULT,
        vbar=True,
        hbar=False,
        **kwargs,
    ):
        super().__init__(master, padding=padding)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        dark_color = '#303030'
        secondary_color = '#444444'
        num_font_color = '#687273'
        text_font_color = '#e8e8e8'
        cursor_color = '#f7d4d4'
        dark_background_color = '#222222'
        secondary_dark_background_color= '#363636'
        selected_background_color = '#444444'
        selected_foreground_color = '#f7d4d4'
        find_background = '#2b2b2b'

        font = ('Arial', '14')
        find_font = ('Arial', '13')
        self._last_line_index = 0  # stores the row index of the previously selected line

        # setup text widget
        self._numbered_text = NumberedText(
            master=self,
            wrap=NONE,
            autostyle=False,
            font=font,
            borderwidth=0,
            highlightthickness=0,
            foreground=num_font_color,
            background=dark_color)

        self._text = CText(
            master=self,
            wrap=NONE,
            undo=True,
            maxundo=-1,
            autoseparators=True,
            autostyle=False,
            font=font,
            insertwidth=3,
            borderwidth=0,
            highlightthickness=0,
            background=dark_color,
            foreground=text_font_color,
            insertbackground=cursor_color,
            selectbackground=secondary_color,
            **kwargs)

        self._numbered_text.tag_configure('tag_selected', foreground=selected_foreground_color)
        self._text.tag_configure('tag_selected', background=selected_background_color)
        self._text.tag_configure('tag_found', background=selected_background_color)

        self._hbar = None
        self._vbar = None

        # delegate text methods to frame
        for method in vars(ttk.Text).keys():
            if any(['pack' in method, 'grid' in method, 'place' in method]):
                pass
            else:
                setattr(self, method, getattr(self._text, method))

        # setup scrollbars
        if vbar is not None:
            self._vbar = AutoScrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._scroll_both,
                orient=VERTICAL,
            )
            self._vbar.grid(row=0, rowspan=2, column=2, sticky=NS)
            self._numbered_text.configure(yscrollcommand=self._update_scroll)
            self._text.configure(yscrollcommand=self._update_scroll)

        if hbar is not None:
            self._hbar = AutoScrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._text.xview,
                orient=HORIZONTAL,
            )
            self._hbar.grid(row=1, column=0, columnspan=2, sticky=EW)
            self._text.configure(xscrollcommand=self._hbar.set)

        self._text.bind('<<TextChanged>>', self._on_change)

        self._numbered_text.grid(row=0, column=0, sticky=NS)
        self._text.grid(row=0, column=1, sticky=NSEW)

        # setup search functionality

        self._search_open = False
        self._find_text = ttk.StringVar(self)
        self._find_frame = ttk.Frame(self._text)

        self._find_entry = tkPlaceholderEntry(
            self._find_frame,
            placeholder='Find..',
            autostyle=False,
            font=find_font,
            borderwidth=0,
            insertwidth=2,
            highlightthickness=0,
            background=find_background,
            foreground=text_font_color,
            insertbackground=cursor_color,
            textvariable=self._find_text)
        self._find_entry.pack(side=LEFT, pady=2, padx=(10, 4))

        #Import the image using PhotoImage function
        self._find_img= ttk.PhotoImage(file='assets/x1.png')

        self._find_close_button = tk.Button(
            self._find_frame,
            autostyle=False,
            image=self._find_img,
            borderwidth=0,
            highlightthickness=0,
            background=dark_background_color,
            activebackground=secondary_dark_background_color,
            relief=FLAT,
            command=self._close_search)
        self._find_close_button.pack(side=LEFT, expand=NO, pady=2, padx=(0, 4))

        self._text.bind_all('<Control-KeyPress-f>', lambda e: self._open_search(), add='+')
        self._text.bind_all('<Escape>', lambda e: self._close_search(), add='+')

    def load_file(self, path:str):
        self.reset()
        with open(path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for row in lines:
                self._text.insert(END, row)

    def _open_search(self):
        self._find_frame.place(relx=0.98, rely=0, anchor=NE, bordermode=OUTSIDE)
        self._search_open = True

    def _close_search(self):
        self._find_frame.place_forget()
        self._search_open = False

    def reset(self):
        # remove selected background from the last selected line
        self._numbered_text.tag_remove('tag_selected', f'{self._last_line_index}.0', f'{self._last_line_index}.end')
        self._text.tag_remove('tag_selected', f'{self._last_line_index}.0', f'{self._last_line_index}.0+1lines')
        self._last_line_index = 0
        # clean text
        self._text.delete('1.0', END)

    def _on_change(self, *_):
        new_num_of_lines = self._text.count('1.0', END, 'displaylines')[0]
        self._numbered_text.set_num_of_lines(new_num_of_lines)

        # remove selected background from the last selected line
        self._numbered_text.tag_remove('tag_selected', f'{self._last_line_index}.0', f'{self._last_line_index}.end')
        self._text.tag_remove('tag_selected', f'{self._last_line_index}.0', f'{self._last_line_index}.0+1lines')
        # get current line row index
        cur_row = self._text.index('insert').split('.')[0]
        self._last_line_index = cur_row
        # set background of currently selected line
        self._numbered_text.tag_add('tag_selected', f'{cur_row}.0', f'{cur_row}.0+1lines')
        self._text.tag_add('tag_selected', f'{cur_row}.0', f'{cur_row}.0+1lines')

    def _scroll_both(self, action, position):
        self._text.yview_moveto(position)
        self._numbered_text.yview_moveto(position)

    def _update_scroll(self, first, last):
        self._text.yview_moveto(first)
        self._numbered_text.yview_moveto(first)
        self._vbar.set(first, last)