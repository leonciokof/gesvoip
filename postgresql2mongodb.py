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
