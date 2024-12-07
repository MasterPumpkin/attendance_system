from django.shortcuts import render
from django.utils.timezone import now
from django.http import JsonResponse
from django.views import View
from clients.models import Client
from employees.models import Employee
from .models import Attendance

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RecordAttendanceView(APIView):
    def post(self, request):
        try:
            # Přijatá data
            data = request.data
            employee_id = data.get('employee_id')
            client_id = data.get('client_id')
            record_type = data.get('type')  # 'checkin' nebo 'checkout'

            # Validace dat
            if not all([employee_id, client_id, record_type]):
                return Response({'error': 'Chybí povinná data!'}, status=status.HTTP_400_BAD_REQUEST)

            # Načtení zaměstnance a klienta
            employee = Employee.objects.get(id=employee_id)
            client = Client.objects.get(id=client_id)

            # Načtení posledního záznamu (pokud existuje)
            last_attendance = Attendance.objects.filter(employee=employee, client=client).order_by('-created_at').first()

            if record_type == 'checkin':
                # Případ 1: Neexistuje žádný záznam -> vytvoříme nový
                if not last_attendance:
                    attendance = Attendance.objects.create(
                        employee=employee,
                        client=client,
                        check_in_time=now(),
                    )
                    return Response({'status': 'success', 'message': 'Check-in vytvořen.'}, status=status.HTTP_201_CREATED)

                # Případ 2: Existuje poslední záznam bez check-out -> ignorujeme
                if not last_attendance.is_closed:
                    return Response({'status': 'ignored', 'message': 'Poslední check-in není uzavřen, nový nebyl vytvořen.'}, status=status.HTTP_200_OK)

                # Případ 3: Vytvoříme nový záznam
                attendance = Attendance.objects.create(
                    employee=employee,
                    client=client,
                    check_in_time=now(),
                )
                return Response({'status': 'success', 'message': 'Check-in vytvořen.'}, status=status.HTTP_201_CREATED)

            elif record_type == 'checkout':
                # Případ 4: Neexistuje záznam s check-in -> ignorujeme
                if not last_attendance or last_attendance.is_closed:
                    return Response({'status': 'ignored', 'message': 'Neexistuje otevřený záznam pro check-out.'}, status=status.HTTP_200_OK)

                # Případ 5: Existuje záznam s check-in -> doplníme check-out
                last_attendance.check_out_time = now()
                last_attendance.is_closed = True  # Uzavření záznamu
                last_attendance.save()
                return Response({'status': 'success', 'message': 'Check-out zapsán.'}, status=status.HTTP_200_OK)

            # Neplatný typ akce
            return Response({'error': 'Neplatný typ akce!'}, status=status.HTTP_400_BAD_REQUEST)

        except Employee.DoesNotExist:
            return Response({'error': 'Zaměstnanec neexistuje!'}, status=status.HTTP_404_NOT_FOUND)
        except Client.DoesNotExist:
            return Response({'error': 'Klient neexistuje!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def qr_scanner_view(request):
    return render(request,'attendances/scan.html')