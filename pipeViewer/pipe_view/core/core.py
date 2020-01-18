
import sys
import string

from wx import Pen, Colour, Font
import wx
import logging
from logging import debug, error, info


class Renderer(object):

    # cdef map[int, Pen] c_pens_map
    # cdef dict __reason_brushes
    # cdef dict __background_brushes
    # cdef object __extensions
    # cdef wxFont c_font
    # cdef wxFont c_bold_font
    # cdef long c_char_width
    # cdef long c_char_height

    # It is preferred to be a long time (>500 uops) before we repeat
    # the same combination of color and symbol.  So it's probably best for these to
    # be relatively prime.  Least common multiple should be much larger than 300.
    # cdef int NUM_REASON_COLORS
    # cdef int NUM_ANNOTATION_COLORS
    # cdef int NUM_ANNOTATION_SYMBOLS
    # cdef char * ANNOTATION_SYMBOL_STRING
    # cdef Pen HIGHLIGHTED_PEN

    def __init__(self, *args):
        self.c_pens_map = {}
        self.__reason_brushes = None
        self.__backgroun_brushes = None
        self.__extensions = None
        self.c_font = None
        self.c_bold_font = None
        self.c_char_width = None
        self.c_char_height = None
        self.NUM_REASON_COLORS = 16
        self.NUM_ANNOTATION_COLORS = 32
        self.NUM_ANNOTATION_SYMBOLS = 52
        self.ANNOTATION_SYMBOL_STRING = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.HIGHLIGHTED_PEN = Pen(Colour(255, 0, 0), 2)

    def __dealloc__(self):
        pass

    def __str__(self):
        return '<pipeViewer Optimized Renderer>'

    def __repr__(self):
        return self.__str__()

    def setBrushes(self, reason_brushes, background_brushes):
        self.__reason_brushes = reason_brushes
        self.__background_brushes = background_brushes

    def setExtensions(self, extensions):
        self.__extensions = extensions

    def __fieldStringColorization(self, string_to_display, field_string):
        # extract what to base color on
        start_idx = string_to_display.find(field_string)
        if start_idx != -1:
            start_idx += len(field_string)
            if start_idx < len(string_to_display) and string_to_display[start_idx] == '{':
                # use everything inside brackets
                start_idx += 1
                next_open = string_to_display.find('{', start_idx)
                next_close = string_to_display.find('}', start_idx)
                # while there is an open at a lower position than a close,
                # skip the close and open (inside pair)
                while next_open < next_close:
                    next_open = string_to_display.find('{', next_open + 1)
                    next_close = string_to_display.find('}', next_close + 1)
                field_value = string_to_display[start_idx:next_close]
            else:
                next_idxs = filter(lambda x: x >= 0, (string_to_display.find(',', start_idx + 1), \
                                                     string_to_display.find(' ', start_idx + 1), \
                                                     string_to_display.find('\n', start_idx + 1)))
                if not next_idxs:
                    field_value = string_to_display[start_idx:]
                else:
                    next_idx = min(next_idxs)
                    field_value = string_to_display[start_idx:next_idx]
            try:
                field_num = int(field_value, 16)
            except ValueError:
                field_num = hash(field_value)
            string_to_display = self.ANNOTATION_SYMBOL_STRING[field_num % self.NUM_ANNOTATION_SYMBOLS]
            background_idx = field_num % self.NUM_ANNOTATION_COLORS
            return string_to_display, self.__background_brushes[background_idx]
        elif string_to_display: # not empty, just can't find
            return '#', None
        else: # empty string
            return string_to_display, None

    def parseAnnotationAndGetColor(self, string_to_display, content_type, field_type = None, field_string = ''):
        '''
        @brief Sets color of background brush and parses annotation according to type.
        '''
        # cdef char * c_seq_id_str
        # cdef unsigned long int c_seq_id
        # cdef char * c_endptr

        brush = None

        #--------------------------------------------------
        # Choose brush color
        # - uop seq ID is first three hex digits
        #
        string_to_display = str(string_to_display)
        if any([content_type == 'auto_color_annotation',
                content_type == 'auto_color_anno_notext',
                content_type == 'auto_color_anno_nomunge']):

            if field_string:
                if field_type == 'string_key' or field_type is None:
                    if content_type == 'auto_color_anno_nomunge':
                        # Preserve current annotation
                        _, brush = self.__fieldStringColorization(string_to_display, field_string)
                    elif content_type == 'auto_color_anno_notext':
                        string_to_display = '' # No text displayed
                        _, brush = self.__fieldStringColorization(string_to_display, field_string)
                    else: # normal annotation mode (display encoded annotation)
                        string_to_display, brush = self.__fieldStringColorization(string_to_display, field_string)

                elif field_type == 'python_exp':
                    try:
                        # Evaluate the user expression
                        info_tuple = eval(field_string, {'anno': string_to_display}, EXPR_NAMESPACE)
                        brush = wx.TheBrushList.FindOrCreateBrush(info_tuple[:3], wx.SOLID) # no guarantees this is fast
                        if len(info_tuple) > 3:
                            string_to_display = str(info_tuple[3])
                        else:
                            pass # Preserve current display string
                    except:
                        error('Error: expression "{}"" raised exception on input "{}":'.format(field_string, string_to_display))
                        error(sys.exc_info())
                        string_to_display = '!'
                elif field_type == 'python_func':
                    func = self.__extensions.GetFunction(field_string)
                    if func:
                        try:
                            info_tuple = func(string_to_display)
                            brush = wx.TheBrushList.FindOrCreateBrush(info_tuple[:3], wx.SOLID)
                            if len(info_tuple) > 3:
                                string_to_display = str(info_tuple[3])
                            else:
                                pass # Preserve current display string
                        except:
                            error('Error: function "{}"" raised exception on input "{}":'.format(field_string, string_to_display))
                            error(sys.exc_info())
                            string_to_display = '!'
                    else:
                        error('Error: function "{}" can not be loaded.'.format(field_string))
                if brush is None:
                    brush = wx.TheBrushList.FindOrCreateBrush(wx.WHITE, wx.SOLID)
                return string_to_display, brush
            else:
                seq_id_str = string_to_display[:3].strip()

                if (len(seq_id_str) >= 3 and seq_id_str[0] == 'R'):
                    #--------------------------------------------------
                    # This is a "reason" instead of a "uop"
                    #
                    if all(char in string.hexdigits for char in seq_id_str):
                        c_seq_id = int(seq_id_str[1], 16) # hex
                        #--------------------------------------------------
                        # We found a valid seq id, so use the new colorization method
                        #

                        if (content_type != 'auto_color_anno_nomunge'):
                            string_to_display = string_to_display[2:]
                        return string_to_display, self.__reason_brushes[c_seq_id % self.NUM_REASON_COLORS]
                else:
                    #--------------------------------------------------
                    # This is not a "reason" and may be a "uop"
                    #
                    if seq_id_str and all(char in string.hexdigits for char in seq_id_str):
                        c_seq_id = int(seq_id_str, 16) # hex

                        #--------------------------------------------------
                        # We found a valid seq id, so use the new colorization method
                        #
                        if (content_type != 'auto_color_anno_nomunge'):
                            c_symbol = self.ANNOTATION_SYMBOL_STRING[c_seq_id % self.NUM_ANNOTATION_SYMBOLS]
                            string_to_display = c_symbol + string_to_display[3:]
                        return string_to_display, self.__background_brushes[c_seq_id % self.NUM_ANNOTATION_COLORS]
        else:
            if all([content_type == 'caption',
                    len(string_to_display) >= 3,
                    string_to_display[:2] == 'C=']):
                c_seq_id_str = string_to_display[2]
                c_seq_id = int(c_seq_id_str, 16) # hex
                c_endptr = 'b'

                if c_endptr != c_seq_id_str:
                    #--------------------------------------------------
                    # We found a valid seq id, so use the new colorization method
                    #
                    #reason_idx = c_seq_id % self.NUM_REASON_COLORS

                    string_to_display = string_to_display[4:]
                    return string_to_display, self.__reason_brushes[c_seq_id % self.NUM_REASON_COLORS]
        return string_to_display, wx.TheBrushList.FindOrCreateBrush(wx.WHITE, wx.SOLID)

    def setFontFromDC(self, dc):

        font = dc.GetFont()
        self.c_font = font
        self.c_bold_font = Font(self.c_font)
        self.c_bold_font.MakeBold()

        if self.c_font.IsFixedWidth():
            wx_str = 'm' # Some character... it's fixed pitch
            size = dc.GetTextExtent(wx_str)
            self.c_char_width, self.c_char_height = size

    def drawInfoRectangle(self,
                            dc,
                            canvas,
                            rect,
                            annotation,
                            missing_needed_loc,
                            content_type,
                            auto_color, # type, basis
                            clip_x, # (start, width)
                            schedule_settings = None,
                            short_format = ''):
                            # schedule_settings: (period_width, 0/1/2 (none/dots/boxed))
        # cdef SwigPyObject * ptr = < SwigPyObject *> dc.this
        # cdef DC * c_dc = < DC * ? > ptr.ptr
        # assert c_dc != NULL

        # cdef int c_x
        # cdef int c_y
        # cdef int c_w
        # cdef int c_h
        # cdef int x_offs

        # cdef char * c_str

        # cdef char c_tmp_char

        # cdef char c_symbol

        # cdef int c_x_adj
        # cdef int c_y_adj

        # cdef int c_num_chars
        # cdef int c_content_str_len
        # cdef Pen old_pen

        x_offs = 0

        c_x, c_y, c_w, c_h = rect

        if missing_needed_loc:
            # Missing location but required one to display. Show with grey hatched background
            string_to_display = ''
            brush = wx.TheBrushList.FindOrCreateBrush((160, 160, 160), wx.CROSSDIAG_HATCH) # no guarantees this is fast
            highlighted = False
        else:
            record = canvas.GetTransactionColor(annotation, content_type, auto_color[0], auto_color[1])
            if record:
                string_to_display, brush, highlighted, _ = record
            else:
                string_to_display, brush, highlighted = canvas.AddColoredTransaction(annotation, content_type, auto_color[0], auto_color[1])

        if highlighted:
            old_pen = dc.GetPen()
            dc.SetPen(self.HIGHLIGHTED_PEN)
            dc.SetFont(self.c_bold_font)
            c_w -= 1
            c_h -= 1
            c_x += 1
            c_y += 1

        # Graph C pointer to brush
        # ptr = < SwigPyObject *> brush.this
        # c_dc.SetBrush((< wxBrush *> ptr.ptr)[0])
        dc.SetBrush(brush)

        if content_type == 'image':
            # Draw an image
            dc.DrawBitmap(canvas.GetMongooseImage(), c_x, c_y)
        else: # auto
            # Draw text clipped to this element

            # Parameters to easily shift the text within a cell.
            c_y_adj = 0
            c_x_adj = 1
            # schedule line drawing code: strict cutting of over-flowing elements
            if schedule_settings:
                # clip long elements
                # don't worry about rendering at -20 or less left
                if c_x + 30 < clip_x[0]:
                    x_offs = c_x - clip_x[0]
                    c_w = c_w + x_offs # can only use upper range
                    c_x = clip_x[0]

                if c_w > clip_x[1]:
                    c_w = clip_x[1] + 30

                # FILL rectangle
                dc.DrawRectangle(c_x, c_y, c_w, c_h)

                period_width, div_type = schedule_settings
                if content_type != 'auto_color_anno_notext' and \
                   string_to_display and \
                   period_width >= self.c_char_width:

                    number_of_divs = c_w / period_width

                    # draw text
                    if div_type == 10 or short_format == 'multi_char': # RULER
                        c_str = string_to_display
                        if 0 <= -x_offs < self.c_char_width * len(string_to_display):
                            dc.DrawText(c_str, c_x + c_x_adj + x_offs, c_y + c_y_adj)
                    else:
                        c_str = string_to_display[0]
                        if 0 <= -x_offs < self.c_char_width:
                            dc.DrawText(c_str, c_x + c_x_adj + x_offs, c_y + c_y_adj)

                    end_coord = c_x + c_w - period_width / 2.0
                    if div_type == 1:
                        y_coord = c_y + c_y_adj + 5
                        curr_x = c_x + c_x_adj + x_offs - 1 + period_width * 1.5
                        while curr_x < end_coord:
                            dc.DrawRectangle(curr_x, y_coord, 2, 2)
                            curr_x += period_width
                    elif div_type == 2:
                        y_coord = c_y + c_y_adj
                        curr_x = c_x + c_x_adj + x_offs
                        if x_offs == 0:
                            curr_x += period_width
                        while curr_x < end_coord:
                            dc.DrawText(c_str, curr_x, y_coord)
                            curr_x += period_width
            else:
                # regular draw
                dc.DrawRectangle(c_x, c_y, c_w, c_h)
                if content_type != 'auto_color_anno_notext':
                    c_str = string_to_display
                    # Truncate text if possible
                    if self.c_char_width != 0:
                        c_num_chars = int(1 + (c_w / self.c_char_width))
                        c_content_str_len = len(c_str)
                        if c_num_chars < c_content_str_len:
                            #c_tmp_char = c_str[c_num_chars]
                            #c_str[c_num_chars] = '\0'.encode('utf-8')
                            dc.DrawText(c_str[:c_num_chars], c_x + c_x_adj, c_y + c_y_adj)
                            #c_str[c_num_chars] = c_tmp_char

                        elif c_content_str_len > 0:
                            dc.DrawText(c_str, c_x + c_x_adj, c_y + c_y_adj)
                    else:
                        dc.DrawText(c_str, c_x + c_x_adj, c_y + c_y_adj)
        if highlighted:
            dc.SetPen(old_pen)
            dc.SetFont(self.c_font)

    def drawElements(self, dc, canvas, tick):
        """
        Draw elements in the list to the given dc
        """
        elements = canvas.GetDrawPairs() # Uses bounds
        xoff, yoff = canvas.GetRenderOffsets()
        _, reason_brushes = canvas.GetBrushes()
        vis_tick = canvas.GetVisibilityTick()

        needs_brush_purge = False
        for pair in elements:
            if pair.GetVisibilityTick() != vis_tick:
                continue # Skip drawing - not visible (probably not on screen)

            string_to_display = pair.GetVal()
            e = pair.GetElement()

            # hack: probably should be handled during update calls
            if e.NeedsDatabase() and e.BrushCacheNeedsPurging():
                e.SetBrushesWerePurged()
                needs_brush_purge = True

            if not e.ShouldDraw():
                continue

            dr = e.GetDrawRoutine()
            if dr:
                # Custom routine.
                dr(e, pair, dc, canvas, tick)
                continue

            (c_x, c_y), (c_w, c_h) = e.GetProperty('position'), e.GetProperty('dimensions')
            (c_x, c_y) = (c_x - xoff, c_y - yoff)

            color = e.GetProperty('color')
            content_type = e.GetProperty('Content')

            c_color = Colour(color[0], color[1], color[2])

            color_rgb = c_color.GetRGB()
            if color_rgb in self.c_pens_map:
                dc.SetPen(self.c_pens_map[color_rgb])
            else:
                c_pen = Pen(c_color, 1)
                self.c_pens_map[color_rgb] = c_pen
                dc.SetPen(c_pen)

            dc.SetClippingRegion(c_x, c_y, c_w, c_h)
            self.drawInfoRectangle(dc, canvas,
                                   (c_x, c_y, c_w, c_h),
                                   string_to_display,
                                   pair.IsMissingLocation(),
                                   content_type,
                                   (e.GetProperty('color_basis_type'), e.GetProperty('auto_color_basis')),
                                   (c_x, c_w))
            dc.DestroyClippingRegion()

        if needs_brush_purge:
            canvas.PurgeBrushCache() # will take care of new render call