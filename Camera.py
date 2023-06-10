import math

import cv2
import keyboard
import mediapipe as mp
import numpy as np


class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

    def _dibujar_maya_facial(self):
        mp_dibujo = mp.solutions.drawing_utils
        confi_dibu = mp_dibujo.DrawingSpec(thickness=1, circle_radius=1)
        return mp_dibujo, confi_dibu

    def _crear_maya_facial(self):
        mp_malla_facial = mp.solutions.face_mesh
        malla_facial = mp_malla_facial.FaceMesh(max_num_faces=1)
        return mp_malla_facial, malla_facial

    def proceso(self):
        mp_dibujo, confi_dibu = self._dibujar_maya_facial()
        mp_malla_facial, malla_facial = self._crear_maya_facial()

        while True:
            ret, frame = self.cap.read()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultados = malla_facial.process(frame_rgb)

            px = []
            py = []
            lista = []
            r = 5
            r = 3
            al, an, c = frame.shape
            face_3d = []
            face_2d = []

            if resultados.multi_face_landmarks:
                for rostros in resultados.multi_face_landmarks:
                    # mp_dibujo.draw_landmarks(frame, rostros, mp_malla_facial.FACEMESH_CONTOURS, confi_dibu, confi_dibu)

                    for id, puntos in enumerate(rostros.landmark):
                        x, y = int(puntos.x * an), int(puntos.y * al)
                        px.append(x)
                        py.append(y)
                        lista.append([id, x, y])
                        if len(lista) == 468:
                            # Ceja Derecha
                            x1, y1 = lista[65][1:]
                            x2, y2 = lista[158][1:]
                            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                            longitud1 = math.hypot(x2 - x1, y2 - y1)

                            # Ceja Izquierda
                            x3, y3 = lista[295][1:]
                            x4, y4 = lista[385][1:]
                            cx2, cy2 = (x3 + x4) // 2, (y3 + y4) // 2
                            longitud2 = math.hypot(x4 - x3, y4 - y3)

                            # Boca Extremos
                            x5, y5 = lista[78][1:]
                            x6, y6 = lista[308][1:]
                            cx3, cy3 = (x5 + x6) // 2, (y5 + y6) // 2
                            longitud3 = math.hypot(x6 - x5, y6 - y5)

                            # Apertura de la boca
                            x7, y7 = lista[13][1:]
                            x8, y8 = lista[14][1:]
                            cx4, cy4 = (x7 + x8) // 2, (y7 + y8) // 2
                            longitud4 = math.hypot(x8 - x7, y8 - y7)

                            if keyboard.is_pressed('ctrl'):
                                if longitud1 > 35 and longitud2 > 35:
                                    movimiento_actual = "atacar"
                                    return movimiento_actual
                                elif 75 < longitud3 < 90 and longitud4 > 10:
                                    movimiento_actual = "comer"
                                    return movimiento_actual

                        if id == 33 or id == 263 or id == 1 or id == 61 or id == 291 or id == 199:
                            if id == 1:
                                nose_2d = (puntos.x * an, puntos.y * al)
                                nose_3d = (puntos.x * an, puntos.y * al, puntos.z * 8000)

                            x, y = int(puntos.x * an), int(puntos.y * al)

                            face_2d.append([x, y])
                            face_3d.append([x, y, puntos.z])

                    face_2d = np.array(face_2d, dtype=np.float64)
                    face_3d = np.array(face_3d, dtype=np.float64)

                    focal_length = 1 * an

                    cam_matrix = np.array([[focal_length, 0, al / 2],
                                           [0, focal_length, an / 2],
                                           [0, 0, 1]])

                    dist_matrix = np.zeros((4, 1), dtype=np.float64)

                    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                    rmat, jac = cv2.Rodrigues(rot_vec)

                    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                    x = angles[0] * 360
                    y = angles[1] * 360

                    if keyboard.is_pressed('ctrl'):
                        if y < -5:
                            movimiento_actual = "derecha"
                            return movimiento_actual
                        elif y > 5:
                            movimiento_actual = "izquierda"
                            return movimiento_actual
                        elif x < -5:
                            movimiento_actual = "abajo"
                            return movimiento_actual
                        elif x > 10:
                            movimiento_actual = "arriba"
                            return movimiento_actual

                    nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix,
                                                                     dist_matrix)

                    p1 = (int(nose_2d[0]), int(nose_2d[1]))
                    p2 = (int(nose_3d_projection[0][0][0]), int(nose_3d_projection[0][0][1]))

                    #cv2.line(frame, p1, p2, (255, 0, 0), 2)

            cv2.imshow("Reconocimiento", frame)
            t = cv2.waitKey(1)

            if t == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()



