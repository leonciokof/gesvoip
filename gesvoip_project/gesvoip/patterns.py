from re import compile

zonas = (
    569, 562, 5632, 5633, 5634, 5635, 5641, 5642, 5643, 5644, 5645,
    5651, 5652, 5653, 5655, 5657, 5658, 5661, 5663, 5664, 5665, 5667,
    5671, 5672, 5673, 5675)
zonas = '|'.join((str(i) for i in zonas))
pattern_zonas = compile('^({0})'.format(zonas))
pattern_569 = compile('^569')
pattern_562 = compile('^562')
pattern_800 = compile('^800')
pattern_4469 = compile('^4469')
pattern_04469 = compile('^04469')
pattern_64469 = compile('^\d{6}4469')
pattern_0234469 = compile('^0234469')
pattern_9 = compile('^(5632|5641|5658|5645|5655|5657|5661|5667|5672)')
pattern_56 = compile('^56')
pattern_564469 = compile('^(564469|44690|02344690)')
pattern_5610 = compile('^(5610|56600|56700|56800)')
