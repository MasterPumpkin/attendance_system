from django.shortcuts import render
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
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
            timestamp = data.get('timestamp')  # ISO 8601 čas

            # Validace dat
            if not all([employee_id, client_id, record_type]):
                return Response({'error': 'Chybí povinná data!'}, status=status.HTTP_400_BAD_REQUEST)

            # Zpracování timestampu
            error_flag = False
            if timestamp:
                try:
                    parsed_time = parse_datetime(timestamp)
                    if not parsed_time or parsed_time.tzinfo is None:
                        raise ValueError("Chybný formát času")
                except ValueError:
                    parsed_time = now()
                    error_flag = True
            else:
                parsed_time = now()
                error_flag = True

            # Načtení zaměstnance a klienta
            employee = Employee.objects.get(id=employee_id)
            client = Client.objects.get(id=client_id)

            # Načtení posledního záznamu (pokud existuje)
            last_attendance = Attendance.objects.filter(employee=employee, client=client).order_by('-created_at').first()

            if record_type == 'checkin':
                if not last_attendance or last_attendance.is_closed:
                    attendance = Attendance.objects.create(
                        employee=employee,
                        client=client,
                        check_in_time=parsed_time,
                        is_error=error_flag,
                    )
                    return Response({'status': 'success', 'message': 'Check-in vytvořen.'}, status=status.HTTP_201_CREATED)
                return Response({'status': 'ignored', 'message': 'Otevřený check-in již existuje.'}, status=status.HTTP_200_OK)

            elif record_type == 'checkout':
                if not last_attendance or last_attendance.is_closed:
                    return Response({'status': 'ignored', 'message': 'Neexistuje otevřený záznam pro check-out.'}, status=status.HTTP_200_OK)

                last_attendance.check_out_time = parsed_time
                # last_attendance.is_closed = True
                last_attendance.is_error = error_flag
                last_attendance.save()
                return Response({'status': 'success', 'message': 'Check-out zapsán.'}, status=status.HTTP_200_OK)

            return Response({'error': 'Neplatný typ akce!'}, status=status.HTTP_400_BAD_REQUEST)

        except Employee.DoesNotExist:
            return Response({'error': 'Zaměstnanec neexistuje!'}, status=status.HTTP_404_NOT_FOUND)
        except Client.DoesNotExist:
            return Response({'error': 'Klient neexistuje!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



def qr_scanner_view(request):
    return render(request,'attendances/scan.html')