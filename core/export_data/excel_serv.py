from openpyxl.styles import Font, PatternFill


def escape_xlsx_char(ch):
    illegal_xlsx_chars = {
        '\x00': '\\x00',  # NULL
        '\x01': '\\x01',  # SOH
        '\x02': '\\x02',  # STX
        '\x03': '\\x03',  # ETX
        '\x04': '\\x04',  # EOT
        '\x05': '\\x05',  # ENQ
        '\x06': '\\x06',  # ACK
        '\x07': '\\x07',  # BELL
        '\x08': '\\x08',  # BS
        '\x0b': '\\x0b',  # VT
        '\x0c': '\\x0c',  # FF
        '\x0e': '\\x0e',  # SO
        '\x0f': '\\x0f',  # SI
        '\x10': '\\x10',  # DLE
        '\x11': '\\x11',  # DC1
        '\x12': '\\x12',  # DC2
        '\x13': '\\x13',  # DC3
        '\x14': '\\x14',  # DC4
        '\x15': '\\x15',  # NAK
        '\x16': '\\x16',  # SYN
        '\x17': '\\x17',  # ETB
        '\x18': '\\x18',  # CAN
        '\x19': '\\x19',  # EM
        '\x1a': '\\x1a',  # SUB
        '\x1b': '\\x1b',  # ESC
        '\x1c': '\\x1c',  # FS
        '\x1d': '\\x1d',  # GS
        '\x1e': '\\x1e',  # RS
        '\x1f': '\\x1f'}  # US

    if ch in illegal_xlsx_chars:
        return illegal_xlsx_chars[ch]

    return ch


def escape_xlsx_char_by_word(word):
    return ''.join(map(escape_xlsx_char, word))


def escape_xlsx_char_by_row(row):
    return (escape_xlsx_char_by_word(col_val) for col_val in row)


def fill_header_style(sheet):
    # apply style font bold and background color gray in the first row
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(fill_type='solid', fgColor='D3D3D3')
