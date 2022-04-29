import time

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from widgets.auto_scrollbar import AutoScrollbar
from widgets.placeholder_entry import tkPlaceholderEntry
from widgets.custom_texts import CText



class Logger(ttk.Frame):
    """Logger widget used to display custom logs and errors."""
    def __init__(
        self,
        master,
        padding=0,
        timestamp=True,
        logLevel=1,
        bootstyle=DEFAULT,
        vbar=True,
        hbar=False,
        **kwargs,
    ):
        """Contract a Logger widget with a parent master.

        STANDARD OPTIONS

        timestamp: If true every log will have a timestamp
        logLevel: the minimum level of logLevel to be displayed

        0 = DEBUG, 1 = INFO, 2=WARNING, 3=ERROR/SUCCESS

        0 should never be used on a live version
        """
        super().__init__(master, padding=padding)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        timestamp_color = 'white'
        info_color = '#ADB5BD'
        warning_color = '#f39c12'
        error_color = '#e74c3c'
        Success_color  = '#00bc8c'


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
        self.log_level = logLevel  # store logLevel as a public var
        self._timestamp = timestamp

        self._text = CText(
            master=self,
            state=DISABLED,
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

        self._text.tag_configure('timestamp_tag', foreground=timestamp_color)
        self._text.tag_configure('tag_selected', foreground=selected_background_color)
        self._text.tag_configure('tag_found', foreground=selected_background_color)

        self._text.tag_configure('tag_debug', foreground=info_color)
        self._text.tag_configure('tag_info', foreground=info_color)
        self._text.tag_configure('tag_warning', foreground=warning_color)
        self._text.tag_configure('tag_error', foreground=error_color)
        self._text.tag_configure('tag_success', foreground=Success_color)

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
                command=self._text.yview,
                orient=VERTICAL,
            )
            self._vbar.grid(row=0, rowspan=2, column=2, sticky=NS)
            self._text.configure(yscrollcommand=self._vbar.set)

        if hbar is not None:
            self._hbar = AutoScrollbar(
                master=self,
                bootstyle=bootstyle,
                command=self._text.xview,
                orient=HORIZONTAL,
            )
            self._hbar.grid(row=1, column=0, columnspan=2, sticky=EW)
            self._text.configure(xscrollcommand=self._hbar.set)

        self._text.bind('<<TextChanged>>', self._onChange)

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
        self._find_button_img= ttk.PhotoImage(file='assets/x1.png')

        self._find_close_button = tk.Button(
            self._find_frame,
            autostyle=False,
            image=self._find_button_img,
            borderwidth=0,
            highlightthickness=0,
            background=dark_background_color,
            activebackground=secondary_dark_background_color,
            relief=FLAT,
            command=self._closeSearch)
        self._find_close_button.pack(side=LEFT, expand=NO, pady=2, padx=(0, 4))

        self._text.bind_all('<Control-KeyPress-f>', lambda e: self._openSearch(), add='+')
        self._text.bind_all('<Escape>', lambda e: self._closeSearch(), add='+')

        self.log('<<LOGGER INITIALIZED>>',INFO)

    def log(self, message:str, logLevel):
        """Add a message to the logger. Each message has a logLevel assosiated
        with it.

        LOG LEVEL OPTIONS

        DEBUG, INFO, WARNING, ERROR, SUCCESS
        """

        timestamp = ''
        if self._timestamp:
            timestamp = time.strftime(f'%H:%M:%S::', time.localtime())

        tag = f'tag_{logLevel}'
        self._text.configure(state=NORMAL)
        self._text.insert(END, timestamp, 'timestamp_tag')
        self._text.insert(END, f'{message}\n', tag)
        self._text.configure(state=DISABLED)

    def _onChange(self, _):
        pass

    def _openSearch(self):
        self._find_frame.place(relx=0.98, rely=0, anchor=NE, bordermode=OUTSIDE)
        self._search_open = True

    def _closeSearch(self):
        self._find_frame.place_forget()
        self._search_open = False