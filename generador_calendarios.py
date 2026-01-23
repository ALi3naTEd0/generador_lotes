import csv
from datetime import datetime, timedelta
from typing import List, Dict
import os

class GeneradorCalendarioCultivo:
    def _agregar_semana_8_9(self, tareas, fechas_semanas, lote, proyecto):
        """Semanas 8-9: Crecimiento tardío"""
        seccion = 'Crecimiento tardío'
        for idx, fechas in enumerate(fechas_semanas, 8):
            num_semana = f'S{idx}'
            if idx == 8:
                # Martes S8: TRASPLANTE CRECIMIENTO TARDIO - CON DEPENDENCIAS
                tarea_trasplante = self._crear_tarea(
                    f'TRASPLANTE CRECIMIENTO TARDIO - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR FERTILIZANTE VERDE 35 GAL CON 14 ML. DE ACIDO (AGUA PURIFICADA)\n    APLICAR 3/4 TBSP. DE BACTERIAS AL SUSTRATO X MACETA\n    TRASPLANTAR\n    REGAR FERTILIZANTE VERDE 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                )
                tarea_trasplante['Blocked By (Dependencies)'] = 'ARMADO MACETA CRECIMINETO TARDIO - SEMANA 7'
                tarea_trasplante['Blocking (Dependencies)'] = 'REGAR TRANSICION MACETA I - SEMANA 10'
                tareas.append(tarea_trasplante)
            else:
                # Martes S9: REGAR MACETA I
                tareas.append(self._crear_tarea(
                    f'REGAR MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR 35 GAL. DE AGUA CON 14 MLT. DE ACIDO\n    REGAR 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
            # Jueves: REGAR MACETA II
            tareas.append(self._crear_tarea(
                f'REGAR MACETA II - SEMANA {idx}',
                seccion, '', fechas[1],
                'INDICACIONES: \nVERIFICAR HUMEDAD DEL SUSTRATO Y REGAR AGUA DE SER REQUERIDO' if idx == 8 else 'INDICACIONES: \nVERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO',
                num_semana, lote, proyecto, seccion, 'SUSTRATO'
            ))
            # Sábado: REGAR MACETA III
            tareas.append(self._crear_tarea(
                f'REGAR MACETA III - SEMANA {idx}',
                seccion, '', fechas[2],
                'INSTRUCCIONES: \nVERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO',
                num_semana, lote, proyecto, seccion, 'SUSTRATO'
            ))
            # FUMIGAR en semanas según tabla (último día laboral)
            nota = self._nota_fumigacion_para_semana(idx)
            if nota:
                fechas_fum = self._ultimo_dia_laboral(fechas)
                tareas.append(self._crear_tarea(
                    f'FUMIGAR - SEMANA {idx}',
                    seccion, 'dgnerazion@gmail.com', fechas_fum,
                    nota,
                    num_semana, lote, proyecto, seccion, 'FOLIAR', start_date=None
                ))
    def __init__(self):
        self.task_id_counter_c = 1211904384322853  # Para archivos _C (clonación)
        self.task_id_counter_d = 1211904167192229  # Para archivos _D (crecimiento)
        
    def solicitar_datos_usuario(self) -> Dict:
        """Solicita al usuario los datos necesarios para generar los calendarios"""
        print("=" * 60)
        print("GENERADOR DE CALENDARIOS DE CULTIVO")
        print("=" * 60)
        
        # Solicitar número de lote
        while True:
            lote_num = input("\n¿Número de lote? (ej: 6, 7, 8, 9): ").strip()
            if lote_num.isdigit():
                break
            print("Por favor ingresa un número válido.")
        
        # Solicitar proyecto
        print("\nProyectos disponibles:")
        print("1. FSM (patrón: Lunes-Miércoles-Viernes)")
        print("2. SMB (patrón: Martes-Jueves-Sábado)")
        print("3. RP (patrón: Martes-Jueves-Sábado)")
        while True:
            proyecto_op = input("Selecciona proyecto (1/2/3): ").strip()
            if proyecto_op in ['1', '2', '3']:
                proyecto = {'1': 'FSM', '2': 'SMB', '3': 'RP'}[proyecto_op]
                break
            print("Opción inválida. Intenta de nuevo.")
        
        # Solicitar fecha inicio para archivo _C (lunes)
        while True:
            fecha_c_str = input("\n¿Fecha de inicio para archivo _C? (formato: YYYY-MM-DD, debe ser LUNES): ").strip()
            try:
                fecha_c = datetime.strptime(fecha_c_str, '%Y-%m-%d')
                if fecha_c.weekday() == 0:  # 0 = Lunes
                    break
                else:
                    print(f"Error: {fecha_c_str} no es lunes. Es {['lunes','martes','miércoles','jueves','viernes','sábado','domingo'][fecha_c.weekday()]}.")
            except ValueError:
                print("Formato inválido. Usa YYYY-MM-DD (ej: 2025-12-29)")
        
        # Calcular fecha inicio para archivo _D según proyecto
        fecha_fin_c = fecha_c + timedelta(days=21 + 5)  # 3 semanas completas + sábado de semana 4
        
        if proyecto == 'FSM':
            # FSM: Siguiente LUNES después de terminar _C
            dias_hasta_lunes = (0 - fecha_fin_c.weekday()) % 7
            if dias_hasta_lunes == 0:
                dias_hasta_lunes = 7
            fecha_d = fecha_fin_c + timedelta(days=dias_hasta_lunes)
            print(f"\nFecha calculada para archivo _D (lunes siguiente): {fecha_d.strftime('%Y-%m-%d')}")
        else:  # SMB o RP
            # SMB/RP: Siguiente MARTES después de terminar _C
            dias_hasta_martes = (1 - fecha_fin_c.weekday()) % 7
            if dias_hasta_martes == 0:
                dias_hasta_martes = 7
            fecha_d = fecha_fin_c + timedelta(days=dias_hasta_martes)
            print(f"\nFecha calculada para archivo _D (martes siguiente): {fecha_d.strftime('%Y-%m-%d')}")
        
        return {
            'lote_num': lote_num,
            'proyecto': proyecto,
            'fecha_c': fecha_c,
            'fecha_d': fecha_d
        }
    
    def generar_fechas_patron(self, fecha_inicio: datetime, patron: str, num_semanas: int) -> List[List[datetime]]:
        """
        Genera fechas según el patrón especificado
        patron puede ser: 'lunes-sabado', 'lunes-miercoles-viernes' o 'martes-jueves-sabado'
        """
        fechas_por_semana = []
        fecha_actual = fecha_inicio
        
        for semana in range(num_semanas):
            if patron == 'lunes-sabado':
                # Lunes a Sábado (6 días)
                fechas_semana = [fecha_actual + timedelta(days=i) for i in range(6)]
            elif patron == 'lunes-miercoles-viernes':
                # Lunes, Miércoles, Viernes (días 0, 2, 4)
                fechas_semana = [
                    fecha_actual,  # Lunes
                    fecha_actual + timedelta(days=2),  # Miércoles
                    fecha_actual + timedelta(days=4)   # Viernes
                ]
            elif patron == 'martes-jueves-sabado':
                # Martes, Jueves, Sábado (días 0, 2, 4)
                fechas_semana = [
                    fecha_actual,  # Martes
                    fecha_actual + timedelta(days=2),  # Jueves
                    fecha_actual + timedelta(days=4)   # Sábado
                ]
            
            fechas_por_semana.append(fechas_semana)
            fecha_actual += timedelta(days=7)
        
        return fechas_por_semana
    
    def generar_fase_clonacion_c(self, lote: str, proyecto: str, fecha_inicio: datetime) -> List[dict]:
        """Genera las 4 semanas de fase de clonación para archivo _C (lunes-sábado)"""
        tareas = []
        fechas_semanas = self.generar_fechas_patron(fecha_inicio, 'lunes-sabado', 4)
        
        for num_semana, fechas in enumerate(fechas_semanas, 1):
            # Primera tarea de la semana (CLONADO o REGAR VERDE A LA RAIZ)
            if num_semana == 1:
                nombre_tarea = "CLONADO DE CHAROLA - SEMANA 1"
                notas = "CLONAR CHAROLA"
                tipo_riego = ""
            else:
                nombre_tarea = f"REGAR VERDE A LA RAIZ - SEMANA {num_semana}"
                # Semana 3 tiene notas cortas, semanas 2 y 4 tienen notas largas
                if num_semana == 3:
                    notas = "INDICACIONES:\nREGAR VERDE A LA RAIZ"
                else:  # Semanas 2 y 4
                    notas = "INDICACIONES:\n    REGAR CLONES CON ATOMIZADOR\n    ABRIR VENTILAS A LA MITAD AL INICIO DE TURNO\n    CERRAR VENTILAS AL FINALIZAR EL TURNO"
                tipo_riego = "A LA RAÍZ"
            
            tareas.append({
                'Task ID': str(self.task_id_counter_c),
                'Section/Column': 'Clonado',
                'Name': nombre_tarea,
                'Assignee': 'dgnerazion@gmail.com',
                'Assignee Email': 'dgnerazion@gmail.com',
                'Start Date': fechas[0].strftime('%Y-%m-%d'),
                'Due Date': fechas[0].strftime('%Y-%m-%d'),
                'Notes': notas,
                'Semana': f'S{num_semana}',
                'Lote': lote,
                'Projects (imported)': proyecto,
                'Etapa': 'Clonación',
                'Tipo de Riego': tipo_riego
            })
            self.task_id_counter_c += 1
            
            # Tareas de riego diario (5 días restantes)
            for i, fecha in enumerate(fechas[1:], 1):
                # Semana 1 tiene notas largas, semanas 2-4 tienen "—"
                if num_semana == 1:
                    notas_riego = "INDICACIONES:\n    REGAR CLONES Y DOMO CON ATOMIZADOR"
                else:
                    notas_riego = "—"
                
                tareas.append({
                    'Task ID': str(self.task_id_counter_c),
                    'Section/Column': 'Clonado',
                    'Name': f"REGAR CLONES {['I','II','III','IV','V'][i-1]} - SEMANA {num_semana}",
                    'Assignee': '',
                    'Assignee Email': '',
                    'Start Date': fecha.strftime('%Y-%m-%d'),
                    'Due Date': fecha.strftime('%Y-%m-%d'),
                    'Notes': notas_riego,
                    'Semana': f'S{num_semana}',
                    'Lote': lote,
                    'Projects (imported)': proyecto,
                    'Etapa': 'Clonación',
                    'Tipo de Riego': 'FOLIAR'  # ✅ AGREGADO
                })
                self.task_id_counter_c += 1
            
            # Última tarea de la semana 4: ARMADO DE MACETA
            if num_semana == 4:
                tareas.append({
                    'Task ID': str(self.task_id_counter_c),
                    'Section/Column': 'Clonado',
                    'Name': 'ARMADO DE MACETA VEG. TEMPRANO - SEMANA 4',
                    'Assignee': 'dgnerazion@gmail.com',
                    'Assignee Email': 'dgnerazion@gmail.com',
                    'Start Date': fechas[-1].strftime('%Y-%m-%d'),
                    'Due Date': fechas[-1].strftime('%Y-%m-%d'),
                    'Notes': 'INTSTRUCCIONES: CORTAR BOLSAS 15X15 AGREGAR SUSTRATO MOLIDO FINO 24 LT AGREGAR SUSTRATO PERLITA 16 LT MEZCLAR PAREJO LLENAR BOLSAS',
                    'Semana': f'S{num_semana}',
                    'Lote': lote,
                    'Projects (imported)': proyecto,
                    'Etapa': 'Clonación',
                    'Tipo de Riego': ''
                })
                self.task_id_counter_c += 1

            # FUMIGACIÓN para la fase de Clonación (semanas 1-4) según tabla
            nota_fum = self._nota_fumigacion_para_semana(num_semana)
            if nota_fum:
                fechas_fum = self._ultimo_dia_laboral(fechas)
                tareas.append({
                    'Task ID': str(self.task_id_counter_c),
                    'Section/Column': 'Clonado',
                    'Name': f'FUMIGAR - SEMANA {num_semana}',
                    'Assignee': 'dgnerazion@gmail.com',
                    'Assignee Email': 'dgnerazion@gmail.com',
                    'Start Date': '',  # Sin start date para fumigación
                    'Due Date': fechas_fum.strftime('%Y-%m-%d'),
                    'Notes': nota_fum,
                    'Semana': f'S{num_semana}',
                    'Lote': lote,
                    'Projects (imported)': proyecto,
                    'Etapa': 'Clonación',
                    'Tipo de Riego': 'FOLIAR'
                })
                self.task_id_counter_c += 1
        
        return tareas
    
    def generar_fase_crecimiento_d(self, lote: str, proyecto: str, fecha_inicio: datetime) -> List[dict]:
        """Genera las semanas 5-22 para archivo _D"""
        tareas = []
        
        # Determinar patrón según proyecto
        if proyecto == 'FSM':
            patron = 'lunes-miercoles-viernes'
        else:  # SMB o RP
            patron = 'martes-jueves-sabado'
        
        # Generar 18 semanas, pero omitir solo la semana de agua en la lógica de floración
        fechas_semanas = self.generar_fechas_patron(fecha_inicio, patron, 18)

        # SEMANA 5: Crecimiento temprano - Trasplante
        self._agregar_semana_5(tareas, fechas_semanas[0], lote, proyecto)

        # SEMANAS 6-7: Crecimiento temprano
        self._agregar_semana_6_7(tareas, fechas_semanas[1:3], lote, proyecto)

        # SEMANAS 8-9: Crecimiento tardío
        self._agregar_semana_8_9(tareas, fechas_semanas[3:5], lote, proyecto)

        # SEMANAS 10-19: Floración
        # indices: fechas_semanas[5] -> S10, ... fechas_semanas[14] -> S19
        self._agregar_semanas_floracion(tareas, fechas_semanas[5:15], lote, proyecto)

        # SEMANAS 20-21: Post-cosecha (secado y trimeado)
        # fechas_semanas[15] -> S20, [16] -> S21
        self._agregar_semanas_postcosecha(tareas, fechas_semanas[15:17], lote, proyecto)
        
        return tareas
    
    def _agregar_semana_5(self, tareas, fechas, lote, proyecto):
        """Semana 5: Trasplante vegetativo temprano"""
        tareas.append(self._crear_tarea(
            'TRASPLANTE VEGETATIVO TEMPRANO - SEMANA 5',
            'Crecimiento temprano',
            'dgnerazion@gmail.com',
            fechas[0],
            'INDICACIONES: \n    PREPARAR FERTILIZANTE VERDE 5 GAL CON 2 ML. DE ACIDO (AGUA PURIFICADA)\n    APLICAR 1 TSP DE BACTERIAS AL SUSTRATO X MACETA\n    TRASPLANTAR\n    REGAR FERTILIZANTE VERDE 1/2 LT. X MACETA',
            'S5', lote, proyecto, 'Crecimiento temprano', 'SUSTRATO'
        ))
        
        tareas.append(self._crear_tarea(
            'REGAR MACETA I - SEMANA 5',
            'Crecimiento temprano',
            '',
            fechas[1],
            'INDICACIONES: \nVERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO',
            'S5', lote, proyecto, 'Crecimiento temprano', 'SUSTRATO'
        ))
        
        tareas.append(self._crear_tarea(
            'REGAR MACETA II - SEMANA 5',
            'Crecimiento temprano',
            '',
            fechas[2],
            'INDICACIONES: \nVERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO',
            'S5', lote, proyecto, 'Crecimiento temprano', 'SUSTRATO'
        ))
        
        tareas.append(self._crear_tarea(
            'FUMIGAR - SEMANA 5',
            'Crecimiento temprano',
            'dgnerazion@gmail.com',
            fechas[2],
            self._nota_fumigacion_para_semana(5),
            'S5', lote, proyecto, 'Crecimiento temprano', 'FOLIAR',
            start_date=None  # Sin start date para fumigación
        ))
    
    def _agregar_semana_6_7(self, tareas, fechas_semanas, lote, proyecto):
        """Semanas 6-7: Crecimiento temprano"""
        seccion = 'Crecimiento temprano'
        for idx, fechas in enumerate(fechas_semanas, 6):
            num_semana = f'S{idx}'
            # Martes: REGAR VERDE o REGAR MACETA I
            if idx == 6:
                tareas.append(self._crear_tarea(
                    f'REGAR VERDE - SEMANA {idx}',
                    'Crecimiento temprano', 'dgnerazion@gmail.com', fechas[0],
                    'INDICACIONES: \nRIEGO CON VERDE 5 GAL',
                    num_semana, lote, proyecto, 'Crecimiento temprano', 'SUSTRATO'
                ))
            else:
                tareas.append(self._crear_tarea(
                    f'REGAR MACETA I - SEMANA {idx}',
                    'Crecimiento temprano', 'dgnerazion@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR AGUA 5 GAL CON 2 MLT. X LT. DE ACIDO (AGUA PURIFICADA)\n    REGAR 1/2 LT X PLANTA',
                    num_semana, lote, proyecto, 'Crecimiento temprano', 'SUSTRATO'
                ))
            
            # Jueves: REGAR MACETA II
            tareas.append(self._crear_tarea(
                f'REGAR MACETA II - SEMANA {idx}',
                'Crecimiento temprano', '', fechas[1],
                'INDICACIONES: \nVERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO',
                num_semana, lote, proyecto, 'Crecimiento temprano', 'SUSTRATO'
            ))
            # Sábado: REGAR MACETA III (faltaba)
            tareas.append(self._crear_tarea(
                f'REGAR MACETA III - SEMANA {idx}',
                'Crecimiento temprano', '', fechas[2],
                'INDICACIONES: \n    VERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO',
                num_semana, lote, proyecto, 'Crecimiento temprano', 'SUSTRATO'
            ))
            # FUMIGAR en semanas 6 y 7 (usar tabla)
            nota_fum = self._nota_fumigacion_para_semana(idx)
            if nota_fum:
                fecha_fum = self._ultimo_dia_laboral(fechas)
                tareas.append(self._crear_tarea(
                    f'FUMIGAR - SEMANA {idx}',
                    'Crecimiento temprano', 'dgnerazion@gmail.com', fecha_fum,
                    nota_fum,
                    num_semana, lote, proyecto, 'Crecimiento temprano', 'FOLIAR', start_date=None
                ))
            # ARMADO MACETA CRECIMINETO TARDIO en semana 7 (día laboral intermedio)
            if idx == 7:
                tareas.append(self._crear_tarea(
                    'ARMADO MACETA CRECIMINETO TARDIO - SEMANA 7',
                    seccion, 'dgnerazion@gmail.com', fechas[1],
                    'INDICACIONES:\n    CORTAR BOLSAS 60X60\n    PREPARAR SUSTRATO, 4 BULTOS MIX3, 8 BULTOS PERLITA, 8 PQ FIBRA DE COCO\n    LLENAR BOLSA 60X60 CON 10 GAL',
                    'S7', lote, proyecto, seccion, 'SUSTRATO'
                ))
            


    def _agregar_semanas_floracion(self, tareas, fechas_semanas, lote, proyecto):
        """Semanas 10-19: Floración (limpia, sin duplicados)."""
        seccion = 'Floración'
        for idx, fechas in enumerate(fechas_semanas, 10):
            # Limitar a la ventana 10..19
            if idx < 10:
                continue
            if idx > 19:
                break

            num_semana = f'S{idx}'
            maceta1_added = False

            # DÍA 1: tareas principales según semana
            if idx == 10:
                tarea = self._crear_tarea(
                    f'REGAR TRANSICION MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR FERTILIZANTE TRANSICION PARA 35 GAL \n    REGAR FERTILIZANTE TRANSICION 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                )
                tarea['Blocked By (Dependencies)'] = 'TRASPLANTE CRECIMIENTO TARDIO - SEMANA 8'
                tareas.append(tarea)
                maceta1_added = True
            elif idx == 11:
                tareas.append(self._crear_tarea(
                    f'REGAR FLOR. TEMPRANO MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR FERTILIZANTE FLOR. TEMPRANO 35 GAL \n    REGAR FERTILIZANTE FLOR. TEMPRANO 2 LT X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
                tareas.append(self._crear_tarea(
                    f'PODA Y TUTORADO - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    '    PODAR PARTE BAJA Y TUTORAR. \n    BARRER Y LIMPIAR EL ÁREA DE TRABAJO AL FINALIZAR LA ACTIVIDAD.',
                    num_semana, lote, proyecto, seccion, 'N/A', start_date=None,
                    blocked_by='SANITIZADO Y PREPARADO DE EQUIPO (TUTORADO) - SEMANA 10'
                ))
                maceta1_added = True
            elif idx == 12:
                tareas.append(self._crear_tarea(
                    f'REGAR AGUA MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR 35 GAL. DE AGUA CON 10 MLT. DE ACIDO (AGUA PURIFICADA)\n    REGAR 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
                tareas.append(self._crear_tarea(
                    f'PODA Y TUTORADO - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    '    PODAR PARTE BAJA Y TUTORAR. \n    BARRER Y LIMPIAR EL ÁREA DE TRABAJO AL FINALIZAR LA ACTIVIDAD.',
                    num_semana, lote, proyecto, seccion, 'N/A', start_date=None
                ))
                maceta1_added = True
            elif idx in [13, 14]:
                tareas.append(self._crear_tarea(
                    f'REGAR FLOR. INTERMEDIO MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR FLOR INTERMEDIO 35 GAL. DE AGUA CON 10 MLT. DE ACIDO (AGUA PURIFICADA)\n    REGAR 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
                maceta1_added = True
            elif idx == 15:
                # Semana 15: AGUA
                tareas.append(self._crear_tarea(
                    f'REGAR AGUA MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR 35 GAL. DE AGUA CON 10 MLT. DE ACIDO (AGUA PURIFICADA)\n    REGAR 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
                maceta1_added = True
            elif idx in [16, 17]:
                tareas.append(self._crear_tarea(
                    f'REGAR FLOR. TARDIO MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    f'INDICACIONES: \n    PREPARAR 35 GAL. DE AGUA CON {10 if idx == 16 else 7} MLT. DE ACIDO (AGUA PURIFICADA)\n    REGAR 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
                maceta1_added = True
                maceta1_added = True
            elif idx == 18:
                tareas.append(self._crear_tarea(
                    f'REGAR MADURACION MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR 35 GAL. DE AGUA CON 7 MLT. DE ACIDO (AGUA PURIFICADA)\n    REGAR 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
                maceta1_added = True
                # Añadir poda del sábado de la semana anterior (S18 Sábado)
                tarea_poda18 = self._crear_tarea(
                    f'PODA DE HOJAS PARA COSECHA - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[2],
                    'INDICACIONES:\n    PODAR TODAS LAS HOJAS CON TALLO',
                    num_semana, lote, proyecto, seccion, '', start_date=None
                )
                # Esta poda de S18 contribuye a la cosecha de la siguiente semana
                tarea_poda18['Blocking (Dependencies)'] = 'COSECHA - SEMANA 19'
                tareas.append(tarea_poda18)
            elif idx == 19:
                tareas.append(self._crear_tarea(
                    f'REGAR FLUSH MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES: \n    PREPARAR 35 GAL. DE AGUA PURIFICADA\n    REGAR 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
                # Poda principal en LUNES de la semana 19
                tarea_poda19 = self._crear_tarea(
                    f'PODA DE HOJAS PARA COSECHA - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[0],
                    'INDICACIONES:\n    PODAR TODAS LAS HOJAS CON TALLO',
                    num_semana, lote, proyecto, seccion, '', start_date=None
                )
                tarea_poda19['Blocking (Dependencies)'] = 'COSECHA - SEMANA 19'
                tareas.append(tarea_poda19)
                # COSECHA y LAVADO en S19
                tarea_cosecha_19 = self._crear_tarea(
                    'COSECHA - SEMANA 19',
                    'Cosecha y post-procesamiento', 'alejandroseguraestrada3@gmail.com', fechas[2],
                    'COSECHAR PLANTAS',
                    num_semana, lote, proyecto, 'Cosecha y post-procesamiento', ''
                )
                # Bloqueada por poda S18 (sábado) y poda S19 (lunes)
                tarea_cosecha_19['Blocked By (Dependencies)'] = 'PODA DE HOJAS PARA COSECHA - SEMANA 18,PODA DE HOJAS PARA COSECHA - SEMANA 19'
                tareas.append(tarea_cosecha_19)
                tareas.append(self._crear_tarea(
                    'LAVADO Y SANITIZADO DE CUARTO - SEMANA 19',
                    'Cosecha y post-procesamiento', 'dgnerazion@gmail.com', fechas[2],
                    'INSTRUCCIONES: \n    LAVAR CON DETERGENTE PISOS Y PAREDES. \n    LAVAR VENTILADORES. \n    LAVAR FILTROS DE CARBON \n    LAVAR DESHUMIDIFICADORES \n    ENJUAGR TODO LO ANTERIOR CON AGUA CON CLORO \n    MANTENIMIENTO A CLIMAS',
                    num_semana, lote, proyecto, 'Cosecha y post-procesamiento', ''
                ))
                maceta1_added = True

            # DÍA 2: REGAR MACETA II y tareas de sanitizado
            if idx == 10:
                tarea_sanitizado = self._crear_tarea(
                    'SANITIZADO Y PREPARADO DE EQUIPO (TUTORADO) - SEMANA 10',
                    seccion, 'alejandroseguraestrada3@gmail.com', fechas[1],
                    'LIMPIAR, SANITIZAR Y PREPARAR EL EQUIPO PARA TUTORADO',
                    num_semana, lote, proyecto, seccion, '', start_date=None
                )
                tarea_sanitizado['Blocking (Dependencies)'] = 'PODA Y TUTORADO - SEMANA 11'
                tareas.append(tarea_sanitizado)

            if idx in [11, 12]:
                tareas.append(self._crear_tarea(
                    f'REGAR MACETA II - SEMANA {idx}',
                    seccion, '', fechas[1],
                    'INDICACIONES: \n    VERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO \n    TUTORADO',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
            elif idx >= 12:
                tareas.append(self._crear_tarea(
                    f'REGAR MACETA II - SEMANA {idx}',
                    seccion, '', fechas[1],
                    f'INDICACIONES: \n    VERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO\n    PREPARAR AGUA 35 GAL CON {10 if idx <= 15 else 7} MLT DE ACIDO \n    REGAR 2 LT POR MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
            else:
                tareas.append(self._crear_tarea(
                    f'REGAR MACETA II - SEMANA {idx}',
                    seccion, '', fechas[1],
                    'INDICACIONES: \nVERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))

            # Si no se creó una tarea para MACETA I en DÍA 1, crearla ahora (ej. S17)
            if not maceta1_added:
                acid = 10 if idx <= 15 else 7
                tareas.append(self._crear_tarea(
                    f'REGAR MACETA I - SEMANA {idx}',
                    seccion, 'alejandroseguraestrada3@gmail.com' if idx <= 15 else '', fechas[0],
                    f'INDICACIONES: \n    VERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO\n    PREPARAR AGUA 35 GAL CON {acid} MLT DE ACIDO (AGUA PURIFICADA)\n    REGAR 2 LT. X MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))

            # DÍA 3: REGAR MACETA III
            if idx >= 12:
                tareas.append(self._crear_tarea(
                    f'REGAR MACETA III - SEMANA {idx}',
                    seccion, '', fechas[2],
                    f'INDICACIONES: \n    VERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO\n    PREPARAR AGUA 35 GAL CON {10 if idx <= 15 else 7} MLT DE ACIDO \n    REGAR 2 LT POR MACETA',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))
            else:
                tareas.append(self._crear_tarea(
                    f'REGAR MACETA III - SEMANA {idx}',
                    seccion, '', fechas[2],
                    'INDICACIONES: \n    VERIFICAR HUMEDAD DEL SUSTRATO Y REGAR DE SER REQUERIDO',
                    num_semana, lote, proyecto, seccion, 'SUSTRATO'
                ))

            # FUMIGAR en semanas 10..15 según tabla (último día laboral)
            nota_fum = self._nota_fumigacion_para_semana(idx)
            if nota_fum:
                fecha_fum = self._ultimo_dia_laboral(fechas)
                tareas.append(self._crear_tarea(
                    f'FUMIGAR - SEMANA {idx}',
                    seccion, 'dgnerazion@gmail.com', fecha_fum,
                    nota_fum,
                    num_semana, lote, proyecto, seccion, 'FOLIAR', start_date=None
                ))

            # (poda de semana 19 ya creada en el bloque de día 1; evitar duplicado)

    def _agregar_semanas_postcosecha(self, tareas, fechas_semanas, lote, proyecto):
        """Semanas 21-22: Secado y Trimeado"""
        # Empezar en S20 (las fechas recibidas corresponden a S20..S21)
        for idx, fechas in enumerate(fechas_semanas, 20):
            num_semana = f'S{idx}'
            seccion = 'Cosecha y post-procesamiento'

            if idx == 20:
                # Semana 20: SECADO (3 días)
                for i, fecha in enumerate(fechas):
                    tareas.append(self._crear_tarea(
                        f'SECADO - SEMANA {idx}',
                        seccion, '', fecha, 'SECADO',
                        num_semana, lote, proyecto, seccion, '', start_date=None
                    ))
            elif idx == 21:
                # Semana 21: TRIMEADO Y EMPACADO (3 días)
                nombres = ['TRIMEADO Y EMPACADO', 'TRIMEADO Y EMPACADO II', 'TRIMEADO Y EMPACADO III']
                for i, fecha in enumerate(fechas):
                    tareas.append(self._crear_tarea(
                        f'{nombres[i]} - SEMANA {idx}',
                        seccion, '', fecha, 'TRIMEADO' if i < 2 else '—',
                        num_semana, lote, proyecto, seccion, '', start_date=None
                    ))

    def _crear_tarea(self, nombre, seccion, email, fecha_due, notas, semana, lote, proyecto, etapa, tipo_riego, start_date='auto', blocked_by='', blocking=''):
        """Helper para crear una tarea"""
        if start_date == 'auto':
            start_date = fecha_due
        
        tarea = {
            'Task ID': str(self.task_id_counter_d),
            'Section/Column': seccion,
            'Name': nombre,
            'Assignee': email,
            'Assignee Email': email,
            'Start Date': start_date.strftime('%Y-%m-%d') if start_date else '',
            'Due Date': fecha_due.strftime('%Y-%m-%d'),
            'Notes': notas,
            'Semana': semana,
            'Lote': lote,
            'Projects (imported)': proyecto,
            'Etapa': etapa,
            'Tipo de Riego': tipo_riego,
            'Blocked By (Dependencies)': blocked_by,
            'Blocking (Dependencies)': blocking
        }
        # Agregar columna 'Cuarto' calculada a partir del número de lote (patrón puede variar por proyecto)
        tarea['Cuarto'] = self._calcular_cuarto(lote, proyecto)
        self.task_id_counter_d += 1
        return tarea

    def _calcular_cuarto(self, lote: str, proyecto: str = '') -> str:
        """Devuelve el identificador de cuarto en formato 'C1', 'C2' o 'C2-C3'.

        Patrón por defecto: L1->C1, L2->C2, L3->C3, L4->C1, etc.
        Para lotes que ocupan dos cuartos se usa el separador '-' (ej. 'C2-C3').
        """
        import re
        m = re.search(r"(\d+)", lote)
        if not m:
            return ''
        n = int(m.group(1))
        mod = n % 3
        # Comportamiento por defecto (no FSM)
        if proyecto == 'FSM':
            # FSM pattern: L1->C2, L2->C1, L3->C3, repeat
            if mod == 1:
                return 'C2'
            elif mod == 2:
                return 'C1'
            else:
                return 'C3'
        elif proyecto == 'RP':
            # RP pattern: odd lot -> C2-C3 (two cuartos), even lot -> C1
            if n % 2 == 1:
                return 'C2-C3'
            else:
                return 'C1'
        else:
            # Default (SMB and others): L1->C1, L2->C2, L3->C3, repeat
            mod = n % 3
            if mod == 1:
                return 'C1'
            elif mod == 2:
                return 'C2'
            else:
                return 'C3'

    def _nota_fumigacion_para_semana(self, idx: int) -> str:
        """Devuelve la nota de fumigación para una semana dada según la tabla de usuario.

        Si no corresponde fumigación, devuelve `None`.
        """
        tabla = {
            1: ("Avalanch + Pacaya", "2 ml/L + 2 ml/L", "Riego + Foliar"),
            2: ("Captan + Pacaya", "1 g/L + 2 ml/L", "Foliar"),
            3: ("Avalanch + Warton", "2 ml/L + 1 ml/L", "Riego + Foliar"),
            4: ("Sultron", "3–4 ml/L", "Foliar"),
            5: ("Pacaya + Avalanch", "2 ml/L + 2 ml/L", "Foliar + Riego"),
            6: ("Warton + Captan", "1.5 ml/L + 1 g/L", "Foliar"),
            7: ("Avalanch + Pacaya", "2 ml/L + 2 ml/L", "Riego + Foliar"),
            8: ("Warton + Avalanch", "1.5 ml/L + 2 ml/L", "Foliar + Riego"),
            9: ("Captan + Pacaya", "1 g/L + 2 ml/L", "Foliar"),
            10: ("Warton", "1.5 ml/L", "Foliar"),
            11: ("Avalanch", "2 ml/L", "Riego"),
            12: ("Pacaya", "2 ml/L", "Foliar"),
            13: ("Avalanch", "2 ml/L", "Riego"),
            14: ("Pacaya", "2 ml/L", "Foliar"),
            15: ("Avalanch", "2 ml/L", "Riego"),
            16: ("Ninguno", "", ""),
            17: ("Ninguno", "", ""),
            18: ("Ninguno", "", ""),
            19: ("Ninguno", "", ""),
            20: ("Ninguno", "", ""),
        }
        info = tabla.get(idx)
        if not info:
            return None
        productos, dosis, via = info
        if productos.lower().startswith('ninguno'):
            return None
        nota = (
            f"FUMIGAR - PRODUCTOS: {productos}\n"
            f"DOSIS: {dosis}\n"
            f"VÍA: {via}\n\n"
            "INSTRUCCIONES: FUMIGAR DE ABAJO HACIA ARRIBA TODO EL LOTE. "
        )
        return nota

    def _ultimo_dia_laboral(self, fechas: List[datetime]) -> datetime:
        """Devuelve el último día del patrón semanal (ej. viernes o sábado).

        Simplemente devuelve la última fecha en la lista `fechas`, que
        corresponde al último día laboral según el patrón de la sucursal.
        """
        return fechas[-1]
    
    def guardar_csv(self, tareas: List[dict], nombre_archivo: str):
        """Guarda las tareas en formato EXACTO de L7_FSM_C.csv"""
        campos = [
            'Task ID', 'Created At', 'Completed At', 'Last Modified', 'Name', 
            'Section/Column', 'Assignee', 'Assignee Email', 'Start Date', 'Due Date',
            'Tags', 'Notes', 'Projects', 'Parent task', 'Blocked By (Dependencies)',
            'Blocking (Dependencies)', 'Semana', 'Lote', 'Projects (imported)', 
            'Cuarto', 'Etapa', 'Tipo de Riego'
        ]
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
            # Encabezado SIN comillas
            f.write(','.join(campos) + '\n')
            
            # Procesar cada tarea
            for tarea in tareas:
                valores = []
                for campo in campos:
                    valor = tarea.get(campo, '')
                    
                    # Completar campos específicos
                    if campo == 'Created At': valor = '2025-11-10'
                    elif campo == 'Completed At': valor = ''
                    elif campo == 'Last Modified': valor = '2025-11-12'
                    elif campo == 'Projects': valor = 'PRUEBA-CLONADO'
                    elif campo in ['Tags', 'Parent task']:
                        valor = ''
                    # NO BORRAR las dependencias, mantener el valor de la tarea
                    elif campo in ['Blocked By (Dependencies)', 'Blocking (Dependencies)']:
                        valor = tarea.get(campo, '')
                    
                    # Formatear valor: con comillas solo si tiene contenido
                    if valor:
                        valores.append(f'"{valor}"')
                    else:
                        valores.append('')
                
                f.write(','.join(valores) + '\n')

    def mostrar_preview_calendario(self, tareas: List[dict], nombre_archivo: str, tipo: str):
        """Muestra un preview del calendario generado"""
        print("\n" + "=" * 80)
        print(f"📅 PREVIEW: {nombre_archivo}")
        print("=" * 80)
        
        # Agrupar tareas por semana
        tareas_por_semana = {}
        for tarea in tareas:
            semana = tarea['Semana']
            if semana not in tareas_por_semana:
                tareas_por_semana[semana] = []
            tareas_por_semana[semana].append(tarea)
        
        # Mostrar resumen
        print(f"\n📊 RESUMEN:")
        print(f"   Total de tareas: {len(tareas)}")
        print(f"   Total de semanas: {len(tareas_por_semana)}")
        print(f"   Tipo de archivo: {tipo}")
        print(f"   Lote: {tareas[0]['Lote']}")
        print(f"   Proyecto: {tareas[0]['Projects (imported)']}")
        
        # Mostrar fechas clave
        fecha_inicio = tareas[0]['Start Date']
        fecha_fin = tareas[-1]['Due Date']
        print(f"   Fecha inicio: {fecha_inicio}")
        print(f"   Fecha fin: {fecha_fin}")
        
        # Mostrar detalle por semana (ordenar numéricamente)
        print(f"\n📋 DETALLE POR SEMANA:")
        # Convertir 'S1', 'S2', etc. a números para ordenar correctamente
        semanas_ordenadas = sorted(tareas_por_semana.keys(), key=lambda x: int(x[1:]))
        
        for semana in semanas_ordenadas:
            tareas_semana = tareas_por_semana[semana]
            print(f"\n   {semana} - {tareas_semana[0]['Etapa']}")
            print(f"   {'─' * 70}")
            
            for tarea in tareas_semana:
                fecha_str = tarea['Due Date']
                # Convertir fecha a día de la semana
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                dia_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'][fecha_obj.weekday()]
                
                nombre_corto = tarea['Name'][:50] + '...' if len(tarea['Name']) > 50 else tarea['Name']
                print(f"   {dia_semana} {fecha_str} | {nombre_corto}")
        
        print("\n" + "=" * 80)
    
    def confirmar_generacion(self) -> bool:
        """Pregunta al usuario si desea continuar con la generación"""
        while True:
            respuesta = input("\n¿Deseas generar estos archivos? (s/n): ").strip().lower()
            if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
                return True
            elif respuesta in ['n', 'no']:
                return False
            print("Por favor responde 's' o 'n'")

# Ejemplo de uso
if __name__ == "__main__":
    generador = GeneradorCalendarioCultivo()
    
    # Solicitar datos al usuario
    datos = generador.solicitar_datos_usuario()
    
    lote_c = f"L{datos['lote_num']} - {datos['proyecto']}"
    lote_d = f"L{datos['lote_num']}"
    
    # Generar tareas (sin guardar aún)
    print(f"\n🔄 Generando preview de archivos...")
    tareas_c = generador.generar_fase_clonacion_c(lote_c, datos['proyecto'], datos['fecha_c'])
    tareas_d = generador.generar_fase_crecimiento_d(lote_d, datos['proyecto'], datos['fecha_d'])
    
    # Mostrar preview de archivo _C
    nombre_archivo_c = f"L{datos['lote_num']}_{datos['proyecto']}_C.csv"
    generador.mostrar_preview_calendario(tareas_c, nombre_archivo_c, "CLONACIÓN")
    
    # Mostrar preview de archivo _D
    nombre_archivo_d = f"L{datos['lote_num']}_{datos['proyecto']}_D.csv"
    generador.mostrar_preview_calendario(tareas_d, nombre_archivo_d, "CRECIMIENTO Y FLORACIÓN")
    
    # Confirmar antes de guardar
    if generador.confirmar_generacion():
        # Guardar archivo _C (en la carpeta actual, no hardcodeado)
        print(f"\n📋 Guardando archivo _C...")
        ruta_completa_c = os.path.join(os.getcwd(), nombre_archivo_c)
        generador.guardar_csv(tareas_c, ruta_completa_c)
        print(f"✅ Archivo guardado: {ruta_completa_c}")
        
        # Guardar archivo _D (en la carpeta actual, no hardcodeado)
        print(f"\n📋 Guardando archivo _D...")
        ruta_completa_d = os.path.join(os.getcwd(), nombre_archivo_d)
        generador.guardar_csv(tareas_d, ruta_completa_d)
        print(f"✅ Archivo guardado: {ruta_completa_d}")
        
        print("\n" + "=" * 60)
        print("✨ ¡Archivos generados exitosamente!")
        print(f"📁 Ubicación: {os.getcwd()}")
        print("=" * 60)
    else:
        print("\n❌ Generación cancelada. No se guardó ningún archivo.")
