def replace_quotes_and_dashes(text):
    text = text.replace(' - ', ' — ')
    quotes = ['"', '„', '“', '”']
    result = []
    temp = 0

    for symbol in text:
        if symbol in quotes and temp == 0:
            symbol = '«'
            temp = 1
        elif symbol in quotes and temp == 1:
            symbol = '»'
            temp = 0
        result.append(symbol)
    return ''.join(result)
