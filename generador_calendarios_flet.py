import flet as ft
from datetime import datetime, timedelta
from generador_calendarios import GeneradorCalendarioCultivo

PROYECTOS = [
    ("FSM", "Lunes-Miércoles-Viernes"),
    ("SMB", "Martes-Jueves-Sábado"),
    ("RP", "Martes-Jueves-Sábado")
]

def main(page: ft.Page):
    page.title = "Generador de Calendarios de Cultivo"
    page.window_width = 600
    page.window_height = 700
    generador = GeneradorCalendarioCultivo()
    # Variables para guardar datos temporales
    datos_guardados = {}

    lote = ft.TextField(label="Número de lote", width=200)
    def actualizar_patron(e=None):
        # Depuración extendida y fallback a e.control.value
        selected = None
        if e:
            if hasattr(e, 'data') and e.data:
                selected = e.data
                print(f"[DEBUG] e.data: {e.data}")
            elif hasattr(e, 'control') and hasattr(e.control, 'value') and e.control.value:
                selected = e.control.value
                print(f"[DEBUG] e.control.value: {e.control.value}")
        if not selected:
            selected = proyecto.value or "FSM"
            print(f"[DEBUG] proyecto.value: {proyecto.value}")
        print(f"[DEBUG] Sucursal seleccionada (final): {selected}")
        for p, pat in PROYECTOS:
            if p == selected:
                patron.value = pat
                print(f"[DEBUG] Patrón actualizado: {pat}")
                break
        page.update()

    proyecto = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value=p[0], label=p[0]) for p in PROYECTOS
        ]),
        value="FSM",
        on_change=actualizar_patron
    )
    # Eliminar botones temporales, ya no necesarios con RadioGroup
    patron = ft.Text(value="Lunes-Miércoles-Viernes", color="blue", selectable=False)
    fecha_c_value = ft.TextField(label="Fecha de inicio (LUNES)", hint_text="YYYY-MM-DD", width=200)
    preview = ft.TextField(label="Preview", multiline=True, min_lines=10, max_lines=20, width=550, read_only=True)
    btn_preview = ft.ElevatedButton("Generar Preview")
    btn_guardar = ft.ElevatedButton("Guardar Archivos", disabled=True)

    def generar_preview(e):
        try:
            lote_num = lote.value.strip()
            if not lote_num.isdigit():
                preview.value = "El número de lote debe ser numérico."
                page.update()
                return
            fecha_c_str = fecha_c_value.value.strip()
            fecha_c_dt = datetime.strptime(fecha_c_str, "%Y-%m-%d")
            if fecha_c_dt.weekday() != 0:
                preview.value = "La fecha debe ser LUNES."
                page.update()
                return
            proyecto_val = proyecto.value
            fecha_fin_c = fecha_c_dt + timedelta(days=21 + 5)
            if proyecto_val == 'FSM':
                dias_hasta_lunes = (0 - fecha_fin_c.weekday()) % 7
                if dias_hasta_lunes == 0:
                    dias_hasta_lunes = 7
                fecha_d = fecha_fin_c + timedelta(days=dias_hasta_lunes)
            else:
                dias_hasta_martes = (1 - fecha_fin_c.weekday()) % 7
                if dias_hasta_martes == 0:
                    dias_hasta_martes = 7
                fecha_d = fecha_fin_c + timedelta(days=dias_hasta_martes)
            datos = {
                'lote_num': lote_num,
                'proyecto': proyecto_val,
                'fecha_c': fecha_c_dt,
                'fecha_d': fecha_d
            }
            lote_c = f"L{lote_num} - {proyecto_val}"
            lote_d = f"L{lote_num}"
            tareas_c = generador.generar_fase_clonacion_c(lote_c, proyecto_val, fecha_c_dt)
            tareas_d = generador.generar_fase_crecimiento_d(lote_d, proyecto_val, fecha_d)
            nombre_archivo_c = f"L{lote_num}_{proyecto_val}_C.csv"
            nombre_archivo_d = f"L{lote_num}_{proyecto_val}_D.csv"
            texto = f"Preview archivo _C: {nombre_archivo_c}\nTareas: {len(tareas_c)}\nPreview archivo _D: {nombre_archivo_d}\nTareas: {len(tareas_d)}\n\nTodas las tareas _C:\n"
            for t in tareas_c:
                texto += f"- {t['Name']} ({t['Due Date']})\n"
            texto += "\nTodas las tareas _D:\n"
            for t in tareas_d:
                texto += f"- {t['Name']} ({t['Due Date']})\n"
            preview.value = texto
            btn_guardar.disabled = False
            # Guardar datos para el botón guardar (en variable local)
            datos_guardados.clear()
            datos_guardados['datos'] = datos
            datos_guardados['tareas_c'] = tareas_c
            datos_guardados['tareas_d'] = tareas_d
            datos_guardados['nombre_archivo_c'] = nombre_archivo_c
            datos_guardados['nombre_archivo_d'] = nombre_archivo_d
        except Exception as ex:
            preview.value = f"Error: {ex}"
        page.update()
    btn_preview.on_click = generar_preview

    def guardar_archivos(e):
        try:
            tareas_c = datos_guardados.get("tareas_c")
            tareas_d = datos_guardados.get("tareas_d")
            nombre_archivo_c = datos_guardados.get("nombre_archivo_c")
            nombre_archivo_d = datos_guardados.get("nombre_archivo_d")
            generador.guardar_csv(tareas_c, nombre_archivo_c)
            generador.guardar_csv(tareas_d, nombre_archivo_d)
            preview.value += f"\nArchivos guardados: {nombre_archivo_c}, {nombre_archivo_d}"
        except Exception as ex:
            preview.value += f"\nError al guardar: {ex}"
        page.update()
    btn_guardar.on_click = guardar_archivos

    page.add(
        ft.Column([
            lote,
            proyecto,
            patron,
            fecha_c_value,
            btn_preview,
            preview,
            btn_guardar
        ], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=10)
    )
    # Actualizar patrón al iniciar
    actualizar_patron()

ft.app(target=main)
