import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import os
from generador_calendarios import GeneradorCalendarioCultivo

class GeneradorCalendarioGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Generador de Calendarios de Cultivo')
        self.geometry('500x500')
        self.generador = GeneradorCalendarioCultivo()
        self._build_widgets()

    def _build_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Lote
        ttk.Label(frame, text='Número de lote:').grid(row=0, column=0, sticky='w')
        self.lote_var = tk.StringVar()
        self.lote_entry = ttk.Entry(frame, textvariable=self.lote_var)
        self.lote_entry.grid(row=0, column=1, sticky='ew')

        # Sucursal
        ttk.Label(frame, text='Sucursal:').grid(row=1, column=0, sticky='w')
        self.sucursal_var = tk.StringVar(value='FSM')
        self.sucursal_combo = ttk.Combobox(frame, textvariable=self.sucursal_var, state='readonly', values=['FSM', 'SMB', 'RP'])
        self.sucursal_combo.grid(row=1, column=1, sticky='ew')
        self.sucursal_combo.bind('<<ComboboxSelected>>', self._actualizar_patron)

        # Patrón (solo lectura)
        self.patron_var = tk.StringVar()
        self._actualizar_patron()  # Inicializar
        ttk.Label(frame, text='Patrón:').grid(row=2, column=0, sticky='w')
        self.patron_label = ttk.Label(frame, textvariable=self.patron_var, foreground='blue')
        self.patron_label.grid(row=2, column=1, sticky='w')

        # Fecha de inicio
        ttk.Label(frame, text='Fecha de inicio (LUNES):').grid(row=3, column=0, sticky='w')
        self.fecha_c_entry = DateEntry(frame, date_pattern='yyyy-mm-dd', width=12)
        self.fecha_c_entry.set_date(datetime.now())
        self.fecha_c_entry.grid(row=3, column=1, padx=5, pady=2, sticky='ew')

        # Botón preview
        self.preview_btn = ttk.Button(frame, text='Generar Preview', command=self.generar_preview)
        self.preview_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Preview
        self.text_preview = tk.Text(frame, height=15, width=60, state='disabled')
        self.text_preview.grid(row=5, column=0, columnspan=2, pady=10)

        # Botón guardar
        self.guardar_btn = ttk.Button(frame, text='Guardar Archivos', command=self.guardar_archivos, state='disabled')
        self.guardar_btn.grid(row=6, column=0, columnspan=2, pady=10)

        frame.columnconfigure(1, weight=1)

    def _actualizar_patron(self, event=None):
        suc = self.sucursal_var.get()
        if suc == 'FSM':
            self.patron_var.set('Lunes-Miércoles-Viernes')
        else:
            self.patron_var.set('Martes-Jueves-Sábado')

    def generar_preview(self):
        lote = self.lote_var.get().strip()
        sucursal = self.sucursal_var.get().strip()
        fecha_c = self.fecha_c_entry.get_date()
        if not lote.isdigit():
            messagebox.showerror('Error', 'El número de lote debe ser un número.')
            return
        if fecha_c.weekday() != 0:
            messagebox.showerror('Error', 'La fecha debe ser LUNES.')
            return
        # Calcular fecha_d
        fecha_fin_c = fecha_c + timedelta(days=21 + 5)
        if sucursal == 'FSM':
            dias_hasta_lunes = (0 - fecha_fin_c.weekday()) % 7
            if dias_hasta_lunes == 0:
                dias_hasta_lunes = 7
            fecha_d = fecha_fin_c + timedelta(days=dias_hasta_lunes)
        else:
            dias_hasta_martes = (1 - fecha_fin_c.weekday()) % 7
            if dias_hasta_martes == 0:
                dias_hasta_martes = 7
            fecha_d = fecha_fin_c + timedelta(days=dias_hasta_martes)
        self.datos = {
            'lote_num': lote,
            'proyecto': sucursal,
            'fecha_c': fecha_c,
            'fecha_d': fecha_d
        }
        lote_c = f"L{lote}"
        lote_d = f"L{lote}"
        self.tareas_c = self.generador.generar_fase_clonacion_c(lote_c, sucursal, fecha_c)
        self.tareas_d = self.generador.generar_fase_crecimiento_d(lote_d, sucursal, fecha_d)
        nombre_archivo_c = f"L{lote}_{sucursal}_C.csv"
        nombre_archivo_d = f"L{lote}_{sucursal}_D.csv"
        # Mostrar preview
        self.text_preview.config(state='normal')
        self.text_preview.delete('1.0', tk.END)
        self.text_preview.insert(tk.END, f"Preview archivo _C: {nombre_archivo_c}\n")
        self.text_preview.insert(tk.END, f"Tareas: {len(self.tareas_c)}\n")
        self.text_preview.insert(tk.END, f"Preview archivo _D: {nombre_archivo_d}\n")
        self.text_preview.insert(tk.END, f"Tareas: {len(self.tareas_d)}\n\n")
        self.text_preview.insert(tk.END, f"Todas las tareas _C:\n")
        for t in self.tareas_c:
            self.text_preview.insert(tk.END, f"- {t['Name']} ({t['Due Date']})\n")
        self.text_preview.insert(tk.END, f"\nTodas las tareas _D:\n")
        for t in self.tareas_d:
            self.text_preview.insert(tk.END, f"- {t['Name']} ({t['Due Date']})\n")
        self.text_preview.config(state='disabled')
        self.guardar_btn.config(state='normal')

    def guardar_archivos(self):
        lote = self.datos['lote_num']
        proyecto = self.datos['proyecto']
        nombre_archivo_c = f"L{lote}_{proyecto}_C.csv"
        nombre_archivo_d = f"L{lote}_{proyecto}_D.csv"
        ruta_c = os.path.join(os.getcwd(), nombre_archivo_c)
        ruta_d = os.path.join(os.getcwd(), nombre_archivo_d)
        self.generador.guardar_csv(self.tareas_c, ruta_c)
        self.generador.guardar_csv(self.tareas_d, ruta_d)
        messagebox.showinfo('Éxito', f'Archivos guardados:\n{ruta_c}\n{ruta_d}')

if __name__ == '__main__':
    try:
        from tkcalendar import DateEntry
    except ImportError:
        import sys
        messagebox.showerror('Falta tkcalendar', 'Instala tkcalendar: pip install tkcalendar')
        sys.exit(1)
    app = GeneradorCalendarioGUI()
    app.mainloop()
