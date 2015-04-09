for c in Compania.objects.all():
    cc = Company(name=c.nombre)
    horario = {}
    for h in c.horario_set.filter(inicio__isnull=False):
        dia = horario.get(h.dia)
        if dia is None:
            horario.update({h.dia: {}})
        tipo = horario.get(h.dia).get(h.tipo)
        if tipo is None:
            horario.get(h.dia).update(
                {h.tipo: {'start': str(h.inicio), 'end': str(h.fin)}})
    cc.schedules = horario
    cc.code = c.codigo
    cc.save()
    for n in c.numeracion_set.all():
        Numeration(zone=n.zona, _range=n.rango, company=cc).save()
Line.objects.all().delete()
for l in Lineas.objects.all():
    if Line.objects.filter(number=int(l.numero)).first() is None:
        l.numero, l.nombre, l.tipo_persona,l.comentarios,l.area,l.comuna
        entity=l.tipo_persona.lower() if l.tipo_persona != '' else None
        city=int(l.comuna) if l.comuna not in [None, ''] else None
        zone=int(l.area) if l.area not in [None, ''] else None
        Line(number=int(l.numero), name=l.nombre, entity=entity,comments=l.comentarios,zone=zone,city=city).save()