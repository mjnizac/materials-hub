# Directorio de Logs

Este directorio contiene los archivos de log de la aplicación Materials Hub.

## Archivos de Log

- `app.log` - Log actual de la aplicación
- `app.log.1` a `app.log.5` - Logs rotados (archivos antiguos)

## Rotación de Logs

Los logs se rotan automáticamente cuando alcanzan 10KB de tamaño. Se mantienen los últimos 5 archivos rotados.

## Limpiar Logs

Para limpiar todos los logs antiguos y mantener solo el actual:

```bash
rosemary clear:log
```

Para limpiar logs más antiguos de N días:

```bash
rosemary clear:log --days 30
```

## Notas

- Los archivos de log están excluidos del control de versiones (`.gitignore`)
- Los logs más antiguos se eliminan automáticamente cuando se supera el límite de archivos rotados
- En desarrollo, los logs también se muestran en consola
